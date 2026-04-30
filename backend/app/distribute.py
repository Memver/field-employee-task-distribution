import logging
import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models import AgentPoint, Employee, Location, TaskType
from app.services.agent_point_events import AgentPointMetricsSnapshot
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

logger = logging.getLogger("uvicorn.error")


@dataclass
class PlannedTask:
    employee_id: int
    agent_point_id: int
    task_type_id: int
    start_time: datetime
    finish_time: datetime
    comment: str = ""


@dataclass
class TaskCandidate:
    task_type: TaskType
    agent_point: AgentPoint
    metrics: AgentPointMetricsSnapshot
    priority_level: int
    type_reason: str


@dataclass
class TaskAssignment:
    employee_id: int
    employee_full_name: str
    agent_point_id: int
    agent_point_address: str | None
    task_type_id: int
    task_type_name: str
    day_index: int
    start_time: datetime
    finish_time: datetime
    reason: str


@dataclass
class TaskUnplaced:
    agent_point_id: int
    agent_point_address: str | None
    task_type_id: int | None
    task_type_name: str | None
    reason: str


@dataclass
class DistributionReport:
    planned_tasks: list[PlannedTask]
    assignments: list[TaskAssignment]
    unplaced: list[TaskUnplaced]


DROP_PENALTY_HOURS_BY_PRIORITY = {
    "high": settings.DROP_PENALTY_HIGH_HOURS,
    "middle": settings.DROP_PENALTY_MIDDLE_HOURS,
    "low": settings.DROP_PENALTY_LOW_HOURS,
}
FIXED_SOLVER_TIME_LIMIT_SECONDS = settings.SOLVER_TIME_LIMIT_SECONDS
RECENT_CONNECTION_DAYS = settings.RECENT_CONNECTION_DAYS


def _select_task_type_for_agent_point(
    agent_point: AgentPoint,
    metrics: AgentPointMetricsSnapshot,
    task_types: list[TaskType],
) -> tuple[TaskType, str] | None:
    task_types_by_name = {task_type.name: task_type for task_type in task_types}
    matched_candidates: list[tuple[TaskType, str]] = []

    connected_yesterday = False
    if agent_point.created_time is not None:
        now_utc = datetime.now(timezone.utc)
        created_time = agent_point.created_time
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        connected_yesterday = (
            now_utc.date() - created_time.date()
        ).days <= RECENT_CONNECTION_DAYS

    if connected_yesterday and "CARDS_DELIVERY" in task_types_by_name:
        matched_candidates.append(
            (
                task_types_by_name["CARDS_DELIVERY"],
                "Точка подключена вчера — назначена доставка карт",
            )
        )
    if (not metrics.is_cards_delivered) and "CARDS_DELIVERY" in task_types_by_name:
        matched_candidates.append(
            (
                task_types_by_name["CARDS_DELIVERY"],
                "Карты ещё не доставлены — назначена доставка карт",
            )
        )

    days_since_last_card_gived = metrics.days_since_last_card_gived
    if (
        days_since_last_card_gived is not None
        and days_since_last_card_gived > 7
        and metrics.approved_applications > 0
        and "SALES_STIMULATION" in task_types_by_name
    ):
        matched_candidates.append(
            (
                task_types_by_name["SALES_STIMULATION"],
                "Карты не выдавались более 7 дней при наличии одобренных заявок — стимулирование продаж",
            )
        )
    if (
        days_since_last_card_gived is not None
        and days_since_last_card_gived > 14
        and "SALES_STIMULATION" in task_types_by_name
    ):
        matched_candidates.append(
            (
                task_types_by_name["SALES_STIMULATION"],
                "Карты не выдавались более 14 дней — стимулирование продаж",
            )
        )

    if (
        metrics.cards_gived > 0
        and metrics.approved_applications > 0
        and (metrics.cards_gived / metrics.approved_applications) < 0.5
        and "AGENT_TRAINING" in task_types_by_name
    ):
        matched_candidates.append(
            (
                task_types_by_name["AGENT_TRAINING"],
                "Низкая конверсия (cards_gived/approved_applications < 0.5) — обучение агента",
            )
        )

    if not matched_candidates:
        return None

    selected_task_type, selected_reason = max(
        matched_candidates,
        key=lambda candidate: (
            candidate[0].priority.level if candidate[0].priority else 0
        ),
    )
    return selected_task_type, selected_reason


def _to_candidate(
    agent_point: AgentPoint,
    task_type: TaskType,
    metrics: AgentPointMetricsSnapshot,
    type_reason: str,
) -> TaskCandidate:
    return TaskCandidate(
        task_type=task_type,
        agent_point=agent_point,
        metrics=metrics,
        priority_level=task_type.priority.level if task_type.priority else 0,
        type_reason=type_reason,
    )


def _employee_full_name(employee: Employee) -> str:
    user = getattr(employee, "user", None)
    if user is None:
        return f"employee #{employee.id}"
    parts = [getattr(user, "surname", "") or "", getattr(user, "name", "") or "", getattr(user, "middle_name", "") or ""]
    full = " ".join(part for part in parts if part).strip()
    return full or f"employee #{employee.id}"


def _agent_point_address(agent_point: AgentPoint) -> str | None:
    location = getattr(agent_point, "location", None)
    if location is None:
        return None
    return getattr(location, "address", None)


def _route_priority_tier(candidate: TaskCandidate, carryover_days: int) -> str:
    """Same tiers as drop penalties: carryover and HIGH priority map to 'high'."""
    if carryover_days > 0:
        return "high"
    if candidate.priority_level >= 110:
        return "high"
    if candidate.priority_level >= 60:
        return "middle"
    return "low"


def _priority_penalty(candidate: TaskCandidate, carryover_days: int) -> int:
    """
    Policy:
    - penalty задается как эквивалент часов дороги;
    - базовый penalty зависит от бизнес-приоритета задачи;
    - перенесённые с прошлых дней задачи (carryover_days > 0) идут как HIGH —
      это требование ТЗ: «оставшиеся переносятся на следующий день с высоким приоритетом».
    """
    if carryover_days > 0 or candidate.priority_level >= 110:
        penalty_hours = (
            DROP_PENALTY_HOURS_BY_PRIORITY["high"]
            * settings.DROP_PENALTY_HIGH_MULTIPLIER
        )
    elif candidate.priority_level >= 60:
        penalty_hours = DROP_PENALTY_HOURS_BY_PRIORITY["middle"]
    else:
        penalty_hours = DROP_PENALTY_HOURS_BY_PRIORITY["low"]

    return penalty_hours * 60 * 60


def _build_distribution_metrics(
    *,
    valid_candidates: list[TaskCandidate],
    assigned_task_nodes: set[int],
    dropped_task_nodes: set[int],
    carryover_days_by_agent_point: dict[int, int],
    total_travel_seconds_to_assigned: int,
    employee_workload_seconds: dict[int, int],
    return_to_start: bool,
) -> dict[str, object]:
    tier_metrics: dict[str, dict[str, int]] = {
        "high": {"eligible": 0, "assigned": 0, "dropped": 0},
        "middle": {"eligible": 0, "assigned": 0, "dropped": 0},
        "low": {"eligible": 0, "assigned": 0, "dropped": 0},
    }
    type_metrics: dict[str, dict[str, int]] = defaultdict(
        lambda: {"eligible": 0, "assigned": 0, "dropped": 0}
    )
    carryover_metrics = {"eligible": 0, "assigned": 0, "dropped": 0}

    for node_idx, candidate in enumerate(valid_candidates):
        carryover_days = carryover_days_by_agent_point.get(candidate.agent_point.id, 0)
        tier = _route_priority_tier(candidate, carryover_days)
        task_type_name = candidate.task_type.name
        is_carryover = carryover_days > 0

        tier_metrics[tier]["eligible"] += 1
        type_metrics[task_type_name]["eligible"] += 1
        if is_carryover:
            carryover_metrics["eligible"] += 1
        if node_idx in assigned_task_nodes:
            tier_metrics[tier]["assigned"] += 1
            type_metrics[task_type_name]["assigned"] += 1
            if is_carryover:
                carryover_metrics["assigned"] += 1
        if node_idx in dropped_task_nodes:
            tier_metrics[tier]["dropped"] += 1
            type_metrics[task_type_name]["dropped"] += 1
            if is_carryover:
                carryover_metrics["dropped"] += 1

    assigned_count = len(assigned_task_nodes)
    avg_travel_minutes = 0.0
    if assigned_count > 0:
        avg_travel_minutes = (total_travel_seconds_to_assigned / assigned_count) / 60
    high_assigned_share = 0.0
    high_assigned_count = tier_metrics["high"]["assigned"]
    if assigned_count > 0:
        high_assigned_share = high_assigned_count / assigned_count
    workload_values = list(employee_workload_seconds.values())
    active_employees = sum(1 for item in workload_values if item > 0)
    workload_min = min(workload_values) if workload_values else 0
    workload_median = int(statistics.median(workload_values)) if workload_values else 0
    workload_max = max(workload_values) if workload_values else 0
    workload_cv = 0.0
    if workload_values:
        workload_mean = sum(workload_values) / len(workload_values)
        if workload_mean > 0:
            workload_cv = statistics.pstdev(workload_values) / workload_mean
    return {
        "totals": {
            "eligible": len(valid_candidates),
            "assigned": assigned_count,
            "dropped": len(dropped_task_nodes),
        },
        "tiers": tier_metrics,
        "task_types": dict(type_metrics),
        "carryover": carryover_metrics,
        "high_assigned_share": round(high_assigned_share, 4),
        "avg_travel_minutes_to_assigned": round(avg_travel_minutes, 2),
        "employees": {
            "total": len(workload_values),
            "active": active_employees,
            "idle": max(0, len(workload_values) - active_employees),
            "workload_seconds": {
                "min": workload_min,
                "median": workload_median,
                "max": workload_max,
                "cv": round(workload_cv, 4),
            },
        },
        "routing_mode": {
            "return_to_start": return_to_start,
        },
    }


def _build_travel_callback(
    manager: pywrapcp.RoutingIndexManager,
    node_location_idx: list[int],
    time_matrix: list[list[float]],
    first_end_node: int,
):
    def travel_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if to_node >= first_end_node:
            return 0
        from_loc = node_location_idx[from_node]
        to_loc = node_location_idx[to_node]
        return max(0, int(float(time_matrix[from_loc][to_loc])))

    return travel_callback


def _build_time_callback(
    manager: pywrapcp.RoutingIndexManager,
    node_location_idx: list[int],
    node_service_seconds: list[int],
    time_matrix: list[list[float]],
    first_end_node: int,
):
    def time_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if to_node >= first_end_node:
            travel_seconds = 0
        else:
            from_loc = node_location_idx[from_node]
            to_loc = node_location_idx[to_node]
            travel_seconds = int(float(time_matrix[from_loc][to_loc]))
        service_seconds = node_service_seconds[from_node]
        return max(0, travel_seconds + service_seconds)

    return time_callback


def _execution_time_hours_to_seconds(execution_time_hours: float) -> int:
    return max(0, int(float(execution_time_hours) * 60 * 60))


def _work_seconds_to_datetime(
    planning_start: datetime, total_work_seconds: int, workday_seconds: int
) -> datetime:
    day_offset = total_work_seconds // workday_seconds
    seconds_in_day = total_work_seconds % workday_seconds
    return planning_start + timedelta(days=day_offset, seconds=seconds_in_day)


def solve(
    *,
    employees: list[Employee],
    agent_points: list[AgentPoint],
    task_types: list[TaskType],
    locations: list[Location],
    time_matrix: list[list[float]],
    planning_start: datetime | None = None,
    horizon_days: int = 3,
    carryover_days_by_agent_point: dict[int, int] | None = None,
    forced_task_type_ids_by_agent_point: dict[int, int] | None = None,
    snapshots_by_agent_point: dict[int, AgentPointMetricsSnapshot] | None = None,
) -> DistributionReport:
    """
    Policy распределения:
    1) тип задачи определяется по правилам ТЗ;
    2) hard constraints: грейд, 8 часов на смену, без обязательного возврата на базу;
    3) objective: минимизация суммарного времени дороги плюс мягкие штрафы за превышение
       «желаемого» времени прибытия по приоритету (SetCumulVarSoftUpperBound на Time);
    4) при дефиците ресурса задачи могут быть отброшены (AddDisjunction): приоритет задаёт
       штраф за drop; перенесённые с прошлых дней считаются как высокий приоритет.
    """
    logger.info(
        "Distribution solver started: employees=%s, agent_points=%s, task_types=%s, locations=%s, horizon_days=%s",
        len(employees),
        len(agent_points),
        len(task_types),
        len(locations),
        horizon_days,
    )
    if not employees or not agent_points or not task_types or not locations:
        return DistributionReport(planned_tasks=[], assignments=[], unplaced=[])

    location_index_by_id = {location.id: idx for idx, location in enumerate(locations)}

    if planning_start is None:
        planning_start = datetime.now(timezone.utc).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
    if carryover_days_by_agent_point is None:
        carryover_days_by_agent_point = {}
    if forced_task_type_ids_by_agent_point is None:
        forced_task_type_ids_by_agent_point = {}
    if snapshots_by_agent_point is None:
        snapshots_by_agent_point = {}
    task_types_by_id = {task_type.id: task_type for task_type in task_types}

    workday_seconds = 8 * 60 * 60
    horizon_days = max(horizon_days, 1)

    unplaced: list[TaskUnplaced] = []
    candidates: list[TaskCandidate] = []
    for agent_point in agent_points:
        metrics = snapshots_by_agent_point.get(agent_point.id, AgentPointMetricsSnapshot())
        forced_task_type_id = forced_task_type_ids_by_agent_point.get(agent_point.id)
        if forced_task_type_id is not None:
            forced_task_type = task_types_by_id.get(forced_task_type_id)
            if forced_task_type is None:
                unplaced.append(
                    TaskUnplaced(
                        agent_point_id=agent_point.id,
                        agent_point_address=_agent_point_address(agent_point),
                        task_type_id=forced_task_type_id,
                        task_type_name=None,
                        reason="Для переносимой задачи не найден task_type",
                    )
                )
                continue
            selection = (
                forced_task_type,
                "Точка в backlog — повторная попытка назначения переносимой задачи",
            )
        else:
            selection = _select_task_type_for_agent_point(agent_point, metrics, task_types)
        if selection is None:
            unplaced.append(
                TaskUnplaced(
                    agent_point_id=agent_point.id,
                    agent_point_address=_agent_point_address(agent_point),
                    task_type_id=None,
                    task_type_name=None,
                    reason="Не подобран тип задачи по правилам",
                )
            )
            continue
        task_type, type_reason = selection
        candidates.append(
            _to_candidate(
                agent_point,
                task_type,
                metrics,
                type_reason,
            )
        )

    if not candidates:
        return DistributionReport(planned_tasks=[], assignments=[], unplaced=unplaced)

    valid_candidates: list[TaskCandidate] = []
    for candidate in candidates:
        task_type = candidate.task_type
        agent_point = candidate.agent_point
        if agent_point.location is None:
            unplaced.append(
                TaskUnplaced(
                    agent_point_id=agent_point.id,
                    agent_point_address=None,
                    task_type_id=task_type.id,
                    task_type_name=task_type.name,
                    reason="У точки не указана локация",
                )
            )
            continue

        if location_index_by_id.get(agent_point.location.id) is None:
            unplaced.append(
                TaskUnplaced(
                    agent_point_id=agent_point.id,
                    agent_point_address=_agent_point_address(agent_point),
                    task_type_id=task_type.id,
                    task_type_name=task_type.name,
                    reason="Локация точки отсутствует в матрице расстояний",
                )
            )
            continue

        min_required_level = task_type.min_grade.level if task_type.min_grade else 0
        eligible_employees = [
            employee
            for employee in employees
            if employee.grade is not None and employee.grade.level >= min_required_level
        ]
        if not eligible_employees:
            unplaced.append(
                TaskUnplaced(
                    agent_point_id=agent_point.id,
                    agent_point_address=_agent_point_address(agent_point),
                    task_type_id=task_type.id,
                    task_type_name=task_type.name,
                    reason="Нет сотрудников с нужным грейдом для типа задачи",
                )
            )
            continue
        valid_candidates.append(candidate)

    if not valid_candidates:
        return DistributionReport(planned_tasks=[], assignments=[], unplaced=unplaced)

    num_tasks = len(valid_candidates)
    vehicle_day_infos: list[tuple[Employee, int]] = []
    for day_idx in range(horizon_days):
        for employee in employees:
            vehicle_day_infos.append((employee, day_idx))
    num_vehicles = len(vehicle_day_infos)
    starts: list[int] = []
    ends: list[int] = []
    node_location_idx: list[int] = []
    node_service_seconds: list[int] = []

    for candidate in valid_candidates:
        loc_idx = location_index_by_id[candidate.agent_point.location.id]
        node_location_idx.append(loc_idx)
        node_service_seconds.append(
            _execution_time_hours_to_seconds(candidate.task_type.execution_time)
        )

    start_node_offset = num_tasks
    end_node_offset = num_tasks + num_vehicles
    for employee, _day_idx in vehicle_day_infos:
        loc_idx = location_index_by_id.get(employee.start_location_id)
        if loc_idx is None:
            loc_idx = 0
        node_location_idx.append(loc_idx)
        node_service_seconds.append(0)
    for employee, _day_idx in vehicle_day_infos:
        loc_idx = location_index_by_id.get(employee.start_location_id)
        if loc_idx is None:
            loc_idx = 0
        node_location_idx.append(loc_idx)
        node_service_seconds.append(0)

    for vehicle_idx in range(num_vehicles):
        starts.append(start_node_offset + vehicle_idx)
        ends.append(end_node_offset + vehicle_idx)

    manager = pywrapcp.RoutingIndexManager(len(node_location_idx), num_vehicles, starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    time_callback_index = routing.RegisterTransitCallback(
        _build_time_callback(
            manager=manager,
            node_location_idx=node_location_idx,
            node_service_seconds=node_service_seconds,
            time_matrix=time_matrix,
            first_end_node=end_node_offset,
        )
    )
    # Optimize by total route load, not only travel: travel + service.
    routing.SetArcCostEvaluatorOfAllVehicles(time_callback_index)
    routing.AddDimension(
        time_callback_index,
        0,
        workday_seconds,
        True,
        "Time",
    )
    time_dimension = routing.GetDimensionOrDie("Time")
    for task_node in range(num_tasks):
        candidate = valid_candidates[task_node]
        min_required_level = (
            candidate.task_type.min_grade.level if candidate.task_type.min_grade else 0
        )
        allowed_vehicles = [
            vehicle_idx
            for vehicle_idx, (employee, _day_idx) in enumerate(vehicle_day_infos)
            if employee.grade is not None and employee.grade.level >= min_required_level
        ]
        task_index = manager.NodeToIndex(task_node)
        if len(allowed_vehicles) < num_vehicles:
            routing.VehicleVar(task_index).SetValues([*allowed_vehicles, -1])

        carryover_days = carryover_days_by_agent_point.get(candidate.agent_point.id, 0)
        routing.AddDisjunction(
            [task_index],
            _priority_penalty(candidate, carryover_days=carryover_days),
        )

        tier = _route_priority_tier(candidate, carryover_days)
        if tier == "high":
            soft_ub = settings.ROUTE_SOFT_DEADLINE_HIGH_SECONDS
            soft_coeff = settings.ROUTE_SOFT_UPPER_VIOLATION_COST_HIGH
        elif tier == "middle":
            soft_ub = settings.ROUTE_SOFT_DEADLINE_MIDDLE_SECONDS
            soft_coeff = settings.ROUTE_SOFT_UPPER_VIOLATION_COST_MIDDLE
        else:
            soft_ub = settings.ROUTE_SOFT_DEADLINE_LOW_SECONDS
            soft_coeff = settings.ROUTE_SOFT_UPPER_VIOLATION_COST_LOW
        if soft_ub is not None and soft_coeff > 0:
            time_dimension.SetCumulVarSoftUpperBound(task_index, soft_ub, soft_coeff)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = FIXED_SOLVER_TIME_LIMIT_SECONDS

    solution = routing.SolveWithParameters(search_parameters)
    if not solution:
        for candidate in valid_candidates:
            unplaced.append(
                TaskUnplaced(
                    agent_point_id=candidate.agent_point.id,
                    agent_point_address=_agent_point_address(candidate.agent_point),
                    task_type_id=candidate.task_type.id,
                    task_type_name=candidate.task_type.name,
                    reason="Планировщик не нашёл решения",
                )
            )
        return DistributionReport(planned_tasks=[], assignments=[], unplaced=unplaced)

    planned_tasks: list[PlannedTask] = []
    assignments: list[TaskAssignment] = []
    dropped_task_nodes: set[int] = set()
    for task_node in range(num_tasks):
        task_index = manager.NodeToIndex(task_node)
        if solution.Value(routing.NextVar(task_index)) == task_index:
            dropped_task_nodes.add(task_node)

    for dropped_node in dropped_task_nodes:
        candidate = valid_candidates[dropped_node]
        unplaced.append(
            TaskUnplaced(
                agent_point_id=candidate.agent_point.id,
                agent_point_address=_agent_point_address(candidate.agent_point),
                task_type_id=candidate.task_type.id,
                task_type_name=candidate.task_type.name,
                reason="Задача отброшена планировщиком (penalty по приоритету)",
            )
        )

    assigned_task_nodes: set[int] = set()
    total_travel_seconds_to_assigned = 0
    employee_workload_seconds: dict[int, int] = {employee.id: 0 for employee in employees}
    for vehicle_idx, (employee, day_idx) in enumerate(vehicle_day_infos):
        index = routing.Start(vehicle_idx)
        route_end_index = routing.End(vehicle_idx)
        route_work_seconds = int(solution.Value(time_dimension.CumulVar(route_end_index)))
        employee_workload_seconds[employee.id] = (
            employee_workload_seconds.get(employee.id, 0) + route_work_seconds
        )
        previous_node = manager.IndexToNode(index)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node < num_tasks and node not in dropped_task_nodes:
                candidate = valid_candidates[node]
                previous_loc_idx = node_location_idx[previous_node]
                current_loc_idx = node_location_idx[node]
                total_travel_seconds_to_assigned += int(
                    float(time_matrix[previous_loc_idx][current_loc_idx])
                )
                assigned_task_nodes.add(node)
                start_seconds_in_shift = int(solution.Value(time_dimension.CumulVar(index)))
                execution_seconds = _execution_time_hours_to_seconds(
                    candidate.task_type.execution_time
                )
                finish_seconds_in_shift = start_seconds_in_shift + execution_seconds
                start_seconds = day_idx * workday_seconds + start_seconds_in_shift
                finish_seconds = day_idx * workday_seconds + finish_seconds_in_shift

                start_time = _work_seconds_to_datetime(
                    planning_start, start_seconds, workday_seconds
                )
                finish_time = _work_seconds_to_datetime(
                    planning_start, finish_seconds, workday_seconds
                )
                planned_tasks.append(
                    PlannedTask(
                        employee_id=employee.id,
                        agent_point_id=candidate.agent_point.id,
                        task_type_id=candidate.task_type.id,
                        start_time=start_time,
                        finish_time=finish_time,
                    )
                )
                full_name = _employee_full_name(employee)
                assignment_reason = (
                    f"{candidate.type_reason}. "
                    f"Назначена сотруднику {full_name} на день {day_idx + 1} из {horizon_days}, "
                    f"слот {start_time:%Y-%m-%d %H:%M}–{finish_time:%H:%M}"
                )
                assignments.append(
                    TaskAssignment(
                        employee_id=employee.id,
                        employee_full_name=full_name,
                        agent_point_id=candidate.agent_point.id,
                        agent_point_address=_agent_point_address(candidate.agent_point),
                        task_type_id=candidate.task_type.id,
                        task_type_name=candidate.task_type.name,
                        day_index=day_idx,
                        start_time=start_time,
                        finish_time=finish_time,
                        reason=assignment_reason,
                    )
                )
                previous_node = node
            index = solution.Value(routing.NextVar(index))

    metrics = _build_distribution_metrics(
        valid_candidates=valid_candidates,
        assigned_task_nodes=assigned_task_nodes,
        dropped_task_nodes=dropped_task_nodes,
        carryover_days_by_agent_point=carryover_days_by_agent_point,
        total_travel_seconds_to_assigned=total_travel_seconds_to_assigned,
        employee_workload_seconds=employee_workload_seconds,
        return_to_start=False,
    )
    logger.info("Distribution solver metrics: %s", metrics)

    planned_tasks.sort(key=lambda item: (item.employee_id, item.start_time))
    assignments.sort(key=lambda item: (item.employee_id, item.start_time))
    return DistributionReport(
        planned_tasks=planned_tasks,
        assignments=assignments,
        unplaced=unplaced,
    )

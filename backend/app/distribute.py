from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.models import AgentPoint, Employee, Location, TaskType
from app.services.agent_point_events import AgentPointMetricsSnapshot
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


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


DROP_PENALTY_HOURS_BY_PRIORITY = {
    "high": 10,
    "middle": 5,
    "low": 2,
}
FIXED_SOLVER_TIME_LIMIT_SECONDS = 60


def _select_task_type_for_agent_point(
    agent_point: AgentPoint,
    metrics: AgentPointMetricsSnapshot,
    task_types: list[TaskType],
) -> TaskType | None:
    task_types_by_name = {task_type.name: task_type for task_type in task_types}

    connected_yesterday = False
    if agent_point.created_time is not None:
        now_utc = datetime.now(timezone.utc)
        created_time = agent_point.created_time
        if created_time.tzinfo is None:
            created_time = created_time.replace(tzinfo=timezone.utc)
        connected_yesterday = (now_utc.date() - created_time.date()).days <= 1

    if (
        (connected_yesterday or not metrics.is_cards_delivered)
        and "CARDS_DELIVERY" in task_types_by_name
    ):
        return task_types_by_name["CARDS_DELIVERY"]

    days_since_last_card_gived = metrics.days_since_last_card_gived
    if (
        (
            (
                days_since_last_card_gived is not None
                and days_since_last_card_gived > 7
                and metrics.approved_applications > 0
            )
            or (days_since_last_card_gived is not None and days_since_last_card_gived > 14)
        )
        and "SALES_STIMULATION" in task_types_by_name
    ):
        return task_types_by_name["SALES_STIMULATION"]

    if (
        metrics.cards_gived > 0
        and metrics.approved_applications > 0
        and (metrics.cards_gived / metrics.approved_applications) < 0.5
        and "AGENT_TRAINING" in task_types_by_name
    ):
        return task_types_by_name["AGENT_TRAINING"]

    if not task_types:
        return None
    return max(
        task_types, key=lambda task_type: task_type.priority.level if task_type.priority else 0
    )


def _to_candidate(
    agent_point: AgentPoint, task_type: TaskType, metrics: AgentPointMetricsSnapshot
) -> TaskCandidate:
    return TaskCandidate(
        task_type=task_type,
        agent_point=agent_point,
        metrics=metrics,
        priority_level=task_type.priority.level if task_type.priority else 0,
    )


def _priority_penalty(candidate: TaskCandidate, carryover_days: int) -> int:
    """
    Policy:
    - penalty задается как эквивалент часов дороги;
    - penalty зависит только от бизнес-приоритета задачи.
    """
    if candidate.priority_level >= 110:
        penalty_hours = DROP_PENALTY_HOURS_BY_PRIORITY["high"]
    elif candidate.priority_level >= 60:
        penalty_hours = DROP_PENALTY_HOURS_BY_PRIORITY["middle"]
    else:
        penalty_hours = DROP_PENALTY_HOURS_BY_PRIORITY["low"]

    return penalty_hours * 60 * 60


def _build_travel_callback(
    manager: pywrapcp.RoutingIndexManager,
    node_location_idx: list[int],
    time_matrix: list[list[float]],
):
    def travel_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        from_loc = node_location_idx[from_node]
        to_loc = node_location_idx[to_node]
        return max(0, int(float(time_matrix[from_loc][to_loc])))

    return travel_callback


def _build_time_callback(
    manager: pywrapcp.RoutingIndexManager,
    node_location_idx: list[int],
    node_service_seconds: list[int],
    time_matrix: list[list[float]],
):
    def time_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        from_loc = node_location_idx[from_node]
        to_loc = node_location_idx[to_node]
        travel_seconds = int(float(time_matrix[from_loc][to_loc]))
        service_seconds = node_service_seconds[from_node]
        return max(0, travel_seconds + service_seconds)

    return time_callback


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
    snapshots_by_agent_point: dict[int, AgentPointMetricsSnapshot] | None = None,
) -> list[PlannedTask]:
    """
    Policy распределения:
    1) тип задачи определяется по правилам ТЗ;
    2) hard constraints: грейд, 8 часов на смену, ежедневный возврат на базу;
    3) objective: минимизация суммарного времени дороги;
    4) при дефиците ресурса задачи могут быть перенесены (drop) по penalty-приоритетам.
    """
    if not employees or not agent_points or not task_types or not locations:
        return []

    location_index_by_id = {location.id: idx for idx, location in enumerate(locations)}

    if planning_start is None:
        planning_start = datetime.now(timezone.utc).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
    if carryover_days_by_agent_point is None:
        carryover_days_by_agent_point = {}
    if snapshots_by_agent_point is None:
        snapshots_by_agent_point = {}

    workday_seconds = 8 * 60 * 60
    horizon_days = max(horizon_days, 1)

    candidates: list[TaskCandidate] = []
    for agent_point in agent_points:
        metrics = snapshots_by_agent_point.get(agent_point.id, AgentPointMetricsSnapshot())
        task_type = _select_task_type_for_agent_point(agent_point, metrics, task_types)
        if task_type is None:
            continue
        candidates.append(_to_candidate(agent_point, task_type, metrics))

    if not candidates:
        return []

    valid_candidates: list[TaskCandidate] = []
    for candidate in candidates:
        task_type = candidate.task_type
        agent_point = candidate.agent_point
        if agent_point.location is None:
            continue

        if location_index_by_id.get(agent_point.location.id) is None:
            continue

        min_required_level = task_type.min_grade.level if task_type.min_grade else 0
        eligible_employees = [
            employee
            for employee in employees
            if employee.grade is not None and employee.grade.level >= min_required_level
        ]
        if not eligible_employees:
            continue
        valid_candidates.append(candidate)

    if not valid_candidates:
        return []

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
        node_service_seconds.append(int(float(candidate.task_type.execution_time) * 60 * 60))

    for employee, _day_idx in vehicle_day_infos:
        loc_idx = location_index_by_id.get(employee.start_location_id)
        if loc_idx is None:
            loc_idx = 0
        node_location_idx.append(loc_idx)
        node_service_seconds.append(0)

    for vehicle_idx in range(num_vehicles):
        depot_node = num_tasks + vehicle_idx
        starts.append(depot_node)
        ends.append(depot_node)

    manager = pywrapcp.RoutingIndexManager(len(node_location_idx), num_vehicles, starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    travel_callback_index = routing.RegisterTransitCallback(
        _build_travel_callback(
            manager=manager,
            node_location_idx=node_location_idx,
            time_matrix=time_matrix,
        )
    )
    routing.SetArcCostEvaluatorOfAllVehicles(travel_callback_index)

    time_callback_index = routing.RegisterTransitCallback(
        _build_time_callback(
            manager=manager,
            node_location_idx=node_location_idx,
            node_service_seconds=node_service_seconds,
            time_matrix=time_matrix,
        )
    )
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
        routing.SetAllowedVehiclesForIndex(allowed_vehicles, task_index)

        carryover_days = carryover_days_by_agent_point.get(candidate.agent_point.id, 0)
        routing.AddDisjunction(
            [task_index],
            _priority_penalty(candidate, carryover_days=carryover_days),
        )

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
        return []

    planned_tasks: list[PlannedTask] = []
    dropped_task_nodes: set[int] = set()
    for task_node in range(num_tasks):
        task_index = manager.NodeToIndex(task_node)
        if solution.Value(routing.NextVar(task_index)) == task_index:
            dropped_task_nodes.add(task_node)

    for vehicle_idx, (employee, day_idx) in enumerate(vehicle_day_infos):
        index = routing.Start(vehicle_idx)
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node < num_tasks and node not in dropped_task_nodes:
                candidate = valid_candidates[node]
                start_seconds_in_shift = int(solution.Value(time_dimension.CumulVar(index)))
                execution_seconds = int(float(candidate.task_type.execution_time) * 60 * 60)
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
                        comment="Auto distributed (OR-Tools rolling horizon)",
                    )
                )
            index = solution.Value(routing.NextVar(index))

    planned_tasks.sort(key=lambda item: (item.employee_id, item.start_time))
    return planned_tasks

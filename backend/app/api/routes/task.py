from typing import Any

from app.api.deps import SessionDep
from app.api.routes.distance_matrix import distance_matrix
from app.models import Message, Task, TaskPublic, TasksPublic
from fastapi import APIRouter
from sqlmodel import func, select

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/",
    response_model=TasksPublic,
)
def read_tasks(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve tasks.
    """

    count_statement = select(func.count()).select_from(Task)
    count = session.exec(count_statement).one()

    statement = select(Task).offset(skip).limit(limit)
    tasks = session.exec(statement).all()

    return TasksPublic(data=tasks, count=count)


@router.get("/{task_id}", response_model=TaskPublic)
def read_task_by_id(task_id: int, session: SessionDep) -> Any:
    """
    Get a specific task by id.
    """
    task = session.get(Task, task_id)
    return task


@router.delete("/{task_id}")
def delete_task(session: SessionDep, task_id: int) -> Message:
    """
    Delete a task.
    """
    task = session.get(Task, task_id)
    # statement = delete(Item).where(col(Item.owner_id) == task_id)
    # session.exec(statement)
    session.delete(task)
    session.commit()
    return Message(message="Task deleted successfully")


@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """

    """Simple Vehicles Routing Problem (VRP).

    This is a sample using the routing library python wrapper to solve a VRP
    problem.
    A description of the problem can be found here:
    http://en.wikipedia.org/wiki/Vehicle_routing_problem.

    Distances are in meters.
    """

    from ortools.constraint_solver import pywrapcp, routing_enums_pb2

    def create_data_model():
        """Stores the data for the problem."""
        data = {}
        data["distance_matrix"] = distance_matrix
        data["num_vehicles"] = 8
        data["starts"] = [0, 0, 0, 1, 1, 1, 2, 2]
        data["ends"] = data["starts"]
        return data

    def print_solution(data, manager, routing, solution):
        """Prints solution on console."""
        print(f"Objective: {solution.ObjectiveValue()}")
        max_route_distance = 0
        for vehicle_id in range(data["num_vehicles"]):
            if not routing.IsVehicleUsed(solution, vehicle_id):
                continue
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            while not routing.IsEnd(index):
                plan_output += f" {manager.IndexToNode(index)} -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            plan_output += f"{manager.IndexToNode(index)}\n"
            plan_output += f"Distance of the route: {route_distance}m\n"
            print(plan_output)
            max_route_distance = max(route_distance, max_route_distance)
        print(f"Maximum of the route distances: {max_route_distance}m")

    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["starts"], data["ends"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = "Distance"
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name,
    )
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("No solution found !")

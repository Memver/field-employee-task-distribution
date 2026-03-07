from app.api.routes.distance_matrix import distance_matrix
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

"""Simple Vehicles Routing Problem (VRP).
    This is a sample using the routing library python wrapper to solve a VRP
    problem.
    A description of the problem can be found here:
    http://en.wikipedia.org/wiki/Vehicle_routing_problem.
    Distances are in meters.
    """


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 8
    data["starts"] = [0, 0, 0, 1, 1, 1, 2, 2]
    data["ends"] = data["starts"]
    # Добавляем ограничение на количество посещений
    data["max_visits_per_vehicle"] = 8
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
        visit_count = 0  # Счетчик посещенных точек
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            plan_output += f" {node} -> "
            visit_count += 1
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m\n"
        plan_output += f"Number of visits: {visit_count - 1}\n"  # -1 чтобы не считать стартовую точку
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
    return int(data["distance_matrix"][from_node][to_node] * 1000)  # Convert to meters


transit_callback_index = routing.RegisterTransitCallback(distance_callback)

# Define cost of each arc.
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Add Distance constraint.
dimension_name = "Distance"
routing.AddDimension(
    transit_callback_index,
    0,  # no slack
    1_040_0000,  # vehicle maximum travel distance (in meters) 130 км * 8 часов
    True,  # start cumul to zero
    dimension_name,
)
distance_dimension = routing.GetDimensionOrDie(dimension_name)
distance_dimension.SetGlobalSpanCostCoefficient(100)


# Добавляем ограничение на количество посещений (каждая точка - 1 посещение)
def visit_callback(from_index, to_index):
    """Returns 1 for each visit (except returning to depot)."""
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    # Возвращаем 1 за каждое посещение, но 0 если возвращаемся в депо
    return 1 if to_node not in [0, 1, 2] else 0


visit_callback_index = routing.RegisterTransitCallback(visit_callback)

# Добавляем dimension для количества посещений
routing.AddDimension(
    visit_callback_index,
    0,  # no slack
    data["max_visits_per_vehicle"],  # максимальное количество посещений на транспорт
    True,  # start cumul to zero
    "Visits",
)

# Setting first solution heuristic.
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
search_parameters.time_limit.seconds = 10  # Добавляем ограничение по времени

# Solve the problem.
solution = routing.SolveWithParameters(search_parameters)

# Print solution on console.
if solution:
    print_solution(data, manager, routing, solution)
else:
    print("No solution found !")

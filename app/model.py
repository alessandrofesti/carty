import pandas as pd
import numpy as np
import googlemaps

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from itertools import product

from ortools.sat.python import cp_model
from itertools import chain
import os
from IPython import display
from pandas import read_excel

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from itertools import product
import pandas as pd

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from data import input_data




def get_latlon_fromaddress(address):
        geolocator = Nominatim(user_agent="Your_Name")
        location = geolocator.geocode(address)
        latlon = [location.latitude, location.longitude]
        return latlon


def get_distance_matrix(input_data):

    latlons = [get_latlon_fromaddress(address) for address in input_data['address']]

    df_combs = pd.DataFrame(list(product(latlons, latlons)))
    df_combs.columns = ['first_item', 'second_item']

    dists = [geodesic(lt, ln).km for lt, ln in zip(df_combs.first_item, df_combs.second_item)]
    df_combs['dist'] = dists

    distance_matrix = []
    df_combs['first_item'] = df_combs['first_item'].apply(lambda x: str(x))

    for lox in df_combs['first_item'].unique():
        mdl = df_combs.loc[df_combs['first_item'] == lox].dist
        list_mdl = list(mdl)
        distance_matrix.append(list_mdl)

    return distance_matrix


def create_data_model(distance_matrix):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_matrix
    data['demands'] = input_data['demands']
    data['num_vehicles'] = len([i for i, e in enumerate(input_data['free_places']) if e != 0])
    data['vehicle_capacities'] = [e for i, e in enumerate(input_data['free_places']) if e != 0]
    data['starts'] = [i for i, e in enumerate(input_data['free_places']) if e != 0]
    data['ends'] = data['num_vehicles']*[[i for i, e in enumerate(input_data['free_places'])][-1]]

    return data


# --- Get distance and time --- #
# api_key = 'AIzaSyCNy9Jg7HdYKLCsBDwRx0XvCwARI8lyTBI'


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Objective: {solution.ObjectiveValue()}')
    total_distance = 0
    total_load = 0
    shifts = {}
    for vehicle_id in range(data['num_vehicles']):
        car_shifts = []
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            car_shifts.append(node_index) # add
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)

        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        car_shifts.append(manager.IndexToNode(index))  # add
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load

        shifts[vehicle_id] = car_shifts  # add

    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))

    return shifts


def main(distance_matrix):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(distance_matrix)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['starts'],
                                           data['ends'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        5000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print('problem solved')
        shifts = print_solution(data, manager, routing, solution)
    else:
        print('problem not solvable')
        shifts = {}

    return shifts


if __name__=='__main__':

    coordinates = get_latlon_fromaddress(address='via oslavia 5 bologna')
    print(coordinates)
    distance_matrix = get_distance_matrix(input_data)
    shifts = main(distance_matrix)
    df_shifts = pd.DataFrame.from_dict(shifts, orient='index')
    print(df_shifts)




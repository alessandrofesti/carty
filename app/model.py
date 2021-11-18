import time

from geopy.geocoders import Nominatim, OpenMapQuest
from geopy.distance import geodesic
from itertools import product
import pandas as pd
import sys

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from geopy.extra.rate_limiter import RateLimiter
import urllib
import requests
import traceback

# city = 'Bologna'
# country = 'Italia'

# TODO:
#   - gestire le location non geolocalizzate bene, ora non funzia
#   - aggiungere distanza

def get_latlon_fromaddress(address, city):
    attempts = 0
    while attempts < 3:
        print(attempts)
        try:
            url = f'https://nominatim.openstreetmap.org/search?format=json&limit=1&street={address}&city={city}' #&country={country}
            headers = {'Accept': 'application/json'}
            params = dict(
                address=address,
                city=city,
                #country=country,
            )
            response = requests.get(url,
                                    headers=headers,
                                    params=params).json()
            latitude = response[0]['lat']
            longitude = response[0]['lon']
            print(f'address is {address} -- lat is {latitude} -- lon is {longitude}')

            attempts = 3
        except Exception as exception:
            print("Exception: {}".format(type(exception).__name__))
            print("Exception message: {}".format(exception))
            print(address)
            latitude = 'cannot geocode'
            longitude = 'cannot geocode'
            attempts += 1

    latlon = [latitude, longitude]

    return latlon


def get_distance_matrix(input_data):
    latlons = [get_latlon_fromaddress(address=address, city=city) for address, city in zip(input_data['address'], input_data['city'])]
    df_geocoded = pd.DataFrame(latlons, columns=['lat', 'lon'])
    df_geocoded['Name'] = input_data['Name'].copy()
    df_geocoded['address'] = input_data['address'].copy()
    df_geocoded['city'] = input_data['city'].copy()
    df_geocoded['demands'] = input_data['demands'].copy()
    df_geocoded['free_places'] = input_data['free_places'].copy()
    df_geocoded = df_geocoded.reset_index()
    # df_geocoded = df_geocoded.sort_values(by='lat')
    df_geocoded.columns = ['index', 'lat', 'lon', 'Name', 'Address', 'City', 'demands', 'free_places']

    latlons_filtered = [[lat, lon] for lat, lon in zip(df_geocoded['lat'], df_geocoded['lon']) if lat != 'cannot geocode']
    df_combs = pd.DataFrame(list(product(latlons_filtered, latlons_filtered)))
    df_combs.columns = ['first_item', 'second_item']

    dists = [geodesic(lt, ln).km for lt, ln in zip(df_combs.first_item, df_combs.second_item)]
    df_combs['dist'] = dists

    distance_matrix = []
    df_combs['first_item'] = df_combs['first_item'].apply(lambda x: str(x))
    df_combs['second_item'] = df_combs['second_item'].apply(lambda x: str(x))

    for lox in df_combs['first_item'].unique():
        mdl = df_combs.loc[df_combs['first_item'] == lox].dist
        list_mdl = list(mdl)
        distance_matrix.append(list_mdl)

    return distance_matrix, df_geocoded


def create_data_model(distance_matrix, df_geocoded):
    """Stores the data for the problem"""
    df_geocoded_f = df_geocoded.loc[df_geocoded['lat'] != 'cannot geocode'].reset_index(drop=True)
    users_not_geocoded = list(df_geocoded.loc[df_geocoded['lat'] == 'cannot geocode'].Name)
    # df_geocoded_f = df_geocoded_f.set_index('index').sort_index(ascending=True)
    data = {}
    data["distance_matrix"] = distance_matrix
    data["demands"] = df_geocoded_f['demands']
    data['num_vehicles'] = len([i for i, e in enumerate(df_geocoded_f['free_places']) if e != 0])
    data['vehicle_capacities'] = [e for i, e in enumerate(df_geocoded_f['free_places']) if e != 0]
    data['starts'] = [i for i, e in enumerate(df_geocoded_f['free_places']) if e != 0]
    data['ends'] = data['num_vehicles']*[[i for i, e in enumerate(df_geocoded_f['free_places'])][-1]]
    data['users_not_geocoded'] = users_not_geocoded

    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    # update data demands because of not geocoded entities
    data['demands'] = data['demands'].reset_index(drop=True)

    # total_distance = 0
    # total_load = 0
    shifts = {}
    for vehicle_id in range(data['num_vehicles']):
        total_distance = 0
        total_load = 0
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
        #print(plan_output)
        total_distance += route_distance
        total_load += route_load

        shifts[vehicle_id] = car_shifts  # add

    shifts['users_not_geocoded'] = data['users_not_geocoded']
    #shifts['total_distance'] = total_distance

    return shifts


def main(distance_matrix, df_geocoded):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(distance_matrix, df_geocoded)

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


# if __name__=='__main__':
#     from data import input_data
#
#     distance_matrix, df_geocoded = get_distance_matrix(input_data)
#     shifts = main(distance_matrix=distance_matrix, df_geocoded=df_geocoded)
#     df_shifts = pd.DataFrame.from_dict(shifts, orient='index')
#     print(df_shifts)




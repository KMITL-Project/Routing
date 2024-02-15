import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import permutations
import os 

class Routing:
    _route_colors = ['r', 'g', 'b', 'c', 'm', 'y']

    def __init__(self, start_point, dist=1000):
        self.graph = ox.graph_from_point(start_point, network_type="all", dist=dist)

    def plot_graph(self, paths):
        route_colors = [self._route_colors[i % len(self._route_colors)] for i in range(len(paths))]
        fig, ax = ox.plot_graph_routes(self.graph, paths, route_colors=route_colors, route_linewidth=6, node_size=3, bgcolor='k')
        plt.show()

    def apply_traffic_data(self, cache_path):
        if os.path.exists(cache_path):
            with open(cache_path) as file:
                traffic_data = json.load(file)

            for u, v, key, data in self.graph.edges(keys=True, data=True):
                edge_key = f"{u},{v}"
                if edge_key in traffic_data:
                    data['time'] = traffic_data[edge_key]
        else:
            print(f"Cache file {cache_path} does not exist. Traffic data not applied.")

    def find_routing(self, destinations=[]):
        nearest_nodes = {}
        for dest in destinations:
            try:
                nearest_node = ox.distance.nearest_nodes(self.graph, dest[1], dest[0])
                nearest_nodes[dest] = nearest_node
            except Exception as e:
                print(f"Error finding nearest node for destination {dest}: {e}. Skipping this destination.")
                continue

        if not nearest_nodes:
            return None, 0, 0  # Handle case where no nearest nodes were found

        best_path, best_length_meter, best_time_sec = self._find_best_route(nearest_nodes)
        return best_path, best_length_meter, best_time_sec

    def _find_best_route(self, nearest_nodes):
        destinations = list(nearest_nodes.keys())
        fixed_start = destinations[0]
        remaining_destinations = destinations[1:]
        best_path, best_length_meter, best_time_sec = None, float('inf'), 0

        for permuted_destination in permutations(remaining_destinations):
            current_permutation = [fixed_start] + list(permuted_destination)
            total_length, total_time, route_paths = self._calculate_route_details(current_permutation, nearest_nodes)

            if total_length < best_length_meter:
                best_length_meter, best_time_sec = total_length, total_time
                best_path = route_paths

        return best_path, best_length_meter, best_time_sec

    def _calculate_route_details(self, destinations, nearest_nodes):
        total_length, total_time, routes = 0, 0, []

        for i in range(len(destinations) - 1):
            origin_node = nearest_nodes[destinations[i]]
            destination_node = nearest_nodes[destinations[i + 1]]
            route = nx.shortest_path(self.graph, origin_node, destination_node, weight='length')
            routes.append(route)

            for j in range(len(route) - 1):
                edge_data = self.graph[route[j]][route[j + 1]][0]
                total_length += edge_data.get('length', 0)
                total_time += edge_data.get('time', 0)

        return total_length, total_time, routes

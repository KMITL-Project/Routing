import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import permutations
from geopy.distance import great_circle
import os 

class Routing:
    _route_colors = ['r', 'g', 'b', 'c', 'm', 'y']
    Dijkstra = "dijkstra"
    AStart = "astar"

    def __init__(self, start_point, dist=1000,algorithm=Dijkstra):
        print(f'\n\nAlgorithm: {algorithm}\n\nDistance: {dist}')
        self.graph = ox.graph_from_point(start_point, network_type="all", dist=dist)
        self.algorithm = algorithm

    def plot_graph(self, route_paths):
        route_colors = [self._route_colors[i % len(self._route_colors)] for i in range(len(route_paths))]
        fig, ax = ox.plot_graph_routes(self.graph, route_paths, route_colors=route_colors, route_linewidth=6, node_size=3, bgcolor='k')
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

        route_coords, best_path, best_length_meter, best_time_sec = self._find_best_route(nearest_nodes)
        return route_coords, best_path, best_length_meter, best_time_sec
    
    def _get_node_coordinates(self,node_ids):
        coords = []
        for node_id in node_ids:
            node_data = self.graph.nodes[node_id]
            coords.append((node_data['y'], node_data['x']))  # Lat, Lon
        return coords
    
    def _haversine(u, v, graph):
        u_latlon = (graph.nodes[u]['y'], graph.nodes[u]['x'])
        v_latlon = (graph.nodes[v]['y'], graph.nodes[v]['x'])
        return great_circle(u_latlon, v_latlon).meters

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

        route_coords = []
        for route in best_path:
            coords = self._get_node_coordinates(route)
            route_coords.append(coords)

        return route_coords,best_path, best_length_meter, best_time_sec

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
    
    def _find_path(self, origin_node, destination_node):
        if self.algorithm == 'astar':
            def heuristic(u, v):
                return self._haversine(u, v, self.graph)
            return nx.astar_path(self.graph, origin_node, destination_node, weight='length',heuristic=heuristic)
        else:  # Default to Dijkstra's algorithm
            return nx.shortest_path(self.graph, origin_node, destination_node, weight='length')

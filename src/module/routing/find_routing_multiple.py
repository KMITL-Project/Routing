import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import json
from itertools import permutations
from geopy.distance import great_circle
import os 
from math import radians, cos, sin, sqrt, atan2, pi

class Routing:
    _route_colors = ['r', 'g', 'b', 'c', 'm', 'y']
    Dijkstra = "dijkstra"
    AStart = "astar"
    R = 6371.0

    def __init__(self, destinations, dist=0,algorithm=AStart):
        self.algorithm = algorithm
        self.destinations = destinations
        if dist == 0:
            print(f'dist = {dist} auto calculate distance')
            dist = self._calculate_max_distance()
        self.graph = ox.graph_from_point(destinations[0], network_type="all", dist=dist)

        print(f'\nAlgorithm: {algorithm}\nDistance: {dist}')

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

    def find_routing(self):
        """
        The function `find_routing` calculates the nearest nodes for a list of destinations and then
        finds the best route based on these nodes.
        :return: The `find_routing` method returns four values: `route_coords`, `best_path`,
        `best_length_meter`, and `best_time_sec`.
        """
        nearest_nodes = {}
        for dest in self.destinations:
            try:
                nearest_node = ox.distance.nearest_nodes(self.graph, dest[1], dest[0])
                nearest_nodes[dest] = nearest_node
            except Exception as e:
                print(f"Error finding nearest node for destination {dest}: {e}. Skipping this destination.")
                continue

        if not nearest_nodes:
            return None, 0, 0  

        route_coords, best_path, best_length_meter, best_time_sec = self._find_best_route(nearest_nodes)
        return route_coords, best_path, best_length_meter, best_time_sec
    

    def _calculate_max_distance(self):
        latitudes = [lat for lat, lon in self.destinations]
        longitudes = [lon for lat, lon in self.destinations]

        if not latitudes or not longitudes or len(latitudes) != len(longitudes) or len(latitudes) < 2:
            return 0

        lat1 = radians(latitudes[0])
        lon1 = radians(longitudes[0])
        max_distance = 0  

        for lat, lon in zip(latitudes[1:], longitudes[1:]):
            lat2 = radians(lat)
            lon2 = radians(lon)

            delta_lat = lat2 - lat1
            delta_lon = lon2 - lon1

            a = sin(delta_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = self.R * c
            max_distance = max(max_distance, distance)
        if max_distance == 0:
            return 0
        return round((max_distance*1000)+1000)
        
    def _get_node_coordinates(self,node_ids):
        coords = []
        for node_id in node_ids:
            node_data = self.graph.nodes[node_id]
            coords.append((node_data['y'], node_data['x']))  # Lat, Lon
        return coords
    
    def _haversine(self,u, v):
        u_latlon = (self.graph.nodes[u]['y'], self.graph.nodes[u]['x'])
        v_latlon = (self.graph.nodes[v]['y'], self.graph.nodes[v]['x'])
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
            route = self._find_path(origin_node=origin_node,destination_node=destination_node,weight="time")
            routes.append(route)

            for j in range(len(route) - 1):
                edge_data = self.graph[route[j]][route[j + 1]][0]
                total_length += edge_data.get('length', 0)
                total_time += edge_data.get('time', 0)

        return total_length, total_time, routes
    
    def _find_path(self, origin_node, destination_node ,weight='length'):
        if self.algorithm == 'astar':
            def heuristic(u, v):
                return self._haversine(u, v)
            return nx.astar_path(self.graph, origin_node, destination_node, weight=weight,heuristic=heuristic)
        else:  # Default to Dijkstra's algorithm
            # return nx.shortest_path(self.graph, origin_node, destination_node, weight=weight)
            return nx.dijkstra_path(self.graph, origin_node, destination_node, weight=weight)


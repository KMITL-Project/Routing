import osmnx as ox
import networkx as nx
from itertools import permutations
import matplotlib.pyplot as plt
import json


class Routing:
    _route_colors = ['r', 'g', 'b', 'c', 'm', 'y']

    def __init__(self , start_point,dist=1000) -> None:
        G = ox.graph_from_point(start_point, network_type="all", dist=dist)
        self.graph = G

    def plot_graph(self,path):
        """
        The function `plot_graph` plots a graph with routes using different colors for each route.
        
        :param path: The `path` parameter is a list of nodes that represent the path or route to be
        plotted on the graph. Each node in the list should be a valid node in the graph
        """
        # Ensure route_colors does not exceed the available colors
        route_colors = [self._route_colors[i % len(self._route_colors)] for i in range(len(path))]
        fig, ax = ox.plot_graph_routes(self.graph, path, route_colors=route_colors, route_linewidth=6, node_size=2, bgcolor='k')
        plt.show()
    
    def _dijkstra_algorithm(self, origin_node, destination_node) :
        route = nx.shortest_path(self.graph, origin_node, destination_node, weight='length')
        return route

    def _astar_algorithm(self, origin_node, destination_node) :
        route = nx.astar_path(self.graph, origin_node, destination_node, weight='length' )
        return route
    
    def apply_traffic_data(self,cache_path):
        traffic_data = []
        with open(cache_path) as file:
            traffic_data = json.load(file)

        for u, v, key, data in self.graph.edges(keys=True, data=True):
            edge_key = f"{u},{v}"
            if edge_key in traffic_data:
                data['time'] = traffic_data[edge_key]

    def find_routing(self,destinations=[]):
        """
        The function finds the best routing path for a given set of destinations using the nearest nodes
        and shortest path algorithms.
        
        :param destinations: The `destinations` parameter is a list of coordinates representing the
        destinations you want to find the routing for. Each destination is a tuple of latitude and
        longitude values
        :return: a tuple containing the best path and the route colors.
        """

        # Compute nearest nodes for all destinations
        nearest_nodes = {}
        for dest in destinations:
            nearest_nodes[dest] = ox.distance.nearest_nodes(self.graph, dest[1], dest[0])

        best_path = None
        best_length_meter = float('inf')
        best_time_sec = float()
        best_lat_long_route = []

        # Iterate over permutations of destinations
        for permuted_destination in permutations(destinations):
            routes = []
            length = 0
            time = 0
            lat_long_route = []
            
            for i in range(len(permuted_destination) - 1):
                origin = permuted_destination[i]
                destination = permuted_destination[i + 1]
                
                # Get nearest nodes from precomputed dictionary
                origin_node = nearest_nodes[origin]
                destination_node = nearest_nodes[destination]
                
                # Find shortest path
                route = self._dijkstra_algorithm(origin_node=origin_node,destination_node=destination_node)
                routes.append(route)
                
                # Accumulate edge weights for path length
                for j in range(len(route) - 1):
                    edge_length = self.graph[route[j]][route[j+1]][0]['length']
                    time += self.graph[route[j]][route[j+1]][0]['time']
                    length += edge_length
                    node_coords = self.graph.nodes[route[j]]['y'], self.graph.nodes[route[j]]['x']
                    lat_long_route.append(node_coords)

                last_node_coords = self.graph.nodes[route[-1]]['y'], self.graph.nodes[route[-1]]['x']
                lat_long_route.append(last_node_coords)

                    

            # Update best path if this permutation is better
            if length < best_length_meter:
                best_length_meter = length
                best_path = routes
                best_time_sec = time
                best_lat_long_route = lat_long_route
                print(lat_long_route)
        
        return (best_path,best_length_meter,best_time_sec)
    


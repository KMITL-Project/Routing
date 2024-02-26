import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import os, json
from geopy.distance import great_circle
from shapely.geometry import LineString, Point
import time
from math import radians, cos, sin, sqrt, atan2

class HeuristicCounter:
    def __init__(self, heuristic):
        self.heuristic = heuristic
        self.reset()

    def __call__(self, u, v):
        self.count += 1
        return self.heuristic(u, v)

    def reset(self):
        self.count = 0

def apply_traffic_data(graph, cache_path):
    if os.path.exists(cache_path):
        with open(cache_path) as file:
            traffic_data = json.load(file)

        for u, v, key, data in graph.edges(keys=True, data=True):
            edge_key = f"{u},{v}"
            if edge_key in traffic_data:
                data['time'] = traffic_data[edge_key]
    else:
        print(f"Cache file {cache_path} does not exist. Traffic data not applied.")

def plot_path(graph, path, color, linewidth, alpha=1):
    for u, v in zip(path[:-1], path[1:]):
        if graph.has_edge(u, v):
            edge_data = graph.get_edge_data(u, v, 0)
            line = edge_data.get('geometry', LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])]))
            plt.plot(*line.xy, color=color, linewidth=linewidth, solid_capstyle='round', alpha=alpha)


def heuristic(u, v):
    u_latlon = (graph.nodes[u]['y'], graph.nodes[u]['x'])
    v_latlon = (graph.nodes[v]['y'], graph.nodes[v]['x'])
    return great_circle(u_latlon, v_latlon).meters
   

def plot_heuristics(graph, end_node):
    for node in graph.nodes:
        h_value = heuristic(node, end_node)
        node_point = Point(graph.nodes[node]['x'], graph.nodes[node]['y'])
        plt.text(node_point.x, node_point.y, f'H:{h_value:.1f}', fontsize=11, ha='center', va='center', color='red')



def plot_surrounding_node_heuristics(graph, path_a, path_b, end_node, color='orange'):
    all_path_nodes = set(path_a + path_b)
    surrounding_nodes = set()

    for node in all_path_nodes:
        neighbors = set(graph.neighbors(node))
        surrounding_nodes.update(neighbors.difference(all_path_nodes))

    for node in all_path_nodes:
        h_value = heuristic(node, end_node)
        node_point = Point(graph.nodes[node]['x'], graph.nodes[node]['y'])
        plt.text(node_point.x, node_point.y, f'H:{h_value:.1f}', fontsize=9, ha='center', va='center', color=color)

    for node in surrounding_nodes:
        h_value = heuristic(node, end_node)
        node_point = Point(graph.nodes[node]['x'], graph.nodes[node]['y'])
        plt.text(node_point.x, node_point.y, f'H:{h_value:.1f}', fontsize=9, ha='center', va='center', color=color)

def plot_surrounding_edges_with_weight(graph, path_a, path_b, ax, color='grey', alpha=0.5):
    nodes = set(path_a + path_b)  
    plotted_edges = set() 
    
    for node in nodes:
        for u, v, data in graph.edges(node, data=True):
            if (u, v) not in plotted_edges and (v, u) not in plotted_edges:  # Check if the edge has not been plotted
                if 'geometry' in data:
                    line = data['geometry']
                else:
                    line = LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])])
                ax.plot(*line.xy, color=color, linewidth=1, alpha=alpha)
                mid_point = line.interpolate(0.5, normalized=True)
                weight = data.get('time', 0) 
                ax.text(mid_point.x,mid_point.y, f"W:{weight:.1f}", color=color, fontsize=11, ha='center', va='center')
                
                plotted_edges.add((u, v))  

graph = ox.graph_from_point((13.795535, 100.707066), network_type="all", dist=5000)
traffic_data_path = "./traffic_data_Monday_1.json"
apply_traffic_data(graph, traffic_data_path)

start_node = 8186043267  # Ensure these are valid node IDs for your graph
end_node = 1696700495

# weight = 'time'
weight = 'length'


start_time_astar = time.time()
shortest_path_astar = nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=weight)
end_time_astar = time.time()

start_time_dijkstra = time.time()
shortest_path_dijkstra = nx.dijkstra_path(graph, start_node, end_node, weight=weight)
end_time_dijkstra = time.time()


fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=10)

plot_path(graph, shortest_path_astar, color="blue", linewidth=2, alpha=1)
plot_path(graph, shortest_path_dijkstra, color="fuchsia", linewidth=4, alpha=0.5)

print(f"Weight:{weight}")
print(f"A*:{end_time_astar - start_time_astar:.4f}")
print(f"D:{end_time_dijkstra - start_time_dijkstra:.4f}")

plot_surrounding_edges_with_weight(graph,shortest_path_astar,shortest_path_dijkstra,ax=ax,color='green')
# plot_heuristics(graph, end_node) 
plot_surrounding_node_heuristics(graph, shortest_path_astar, shortest_path_dijkstra, end_node, color='orange')

plt.show()

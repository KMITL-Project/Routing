import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
from geopy.distance import great_circle
import random
import json
import time
import uuid

def configure_osmnx():
    """Configure OSMnx settings."""
    ox.config(use_cache=True)

def load_and_apply_traffic_data(graph, traffic_data_path):
    """Load traffic data from a JSON file and apply it to the graph."""
    with open(traffic_data_path, 'r') as file:
        traffic_data = json.load(file)

    for u, v, key, data in graph.edges(keys=True, data=True):
        edge_key = f"{u},{v}"
        if edge_key in traffic_data:
            data['time'] = traffic_data[edge_key]

def find_and_plot_routes(graph, start_node, end_node, weight='time'):
    """Find routes, plot them, and compare their lengths, times, and execution times."""
    # Define heuristic for A* path
    heuristic = lambda u, v: great_circle((graph.nodes[u]['y'], graph.nodes[u]['x']), (graph.nodes[v]['y'], graph.nodes[v]['x'])).meters

    # heuristic = lambda u, v: 0

    
    # A* Algorithm
    start_time_astar = time.time()
    path_astar = nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=weight)
    end_time_astar = time.time()
    astar_exec_time = end_time_astar - start_time_astar

    # Dijkstra's Algorithm
    start_time_dijkstra = time.time()
    # path_dijkstra = nx.shortest_path(graph, start_node, end_node, weight=weight, method="dijkstra")
    path_dijkstra = nx.dijkstra_path(graph, start_node, end_node, weight=weight)
    end_time_dijkstra = time.time()
    dijkstra_exec_time = end_time_dijkstra - start_time_dijkstra

    print(f"A* execution time: {astar_exec_time:.4f} seconds")
    print(f"Dijkstra's execution time: {dijkstra_exec_time:.4f} seconds")

    # Plot paths
    fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=0)
    plot_path(ax, graph, path_astar, 'blue', 4)
    plot_path(ax, graph, path_dijkstra, 'red', 2, alpha=0.5)
    plt.show()

    # Print execution times

def plot_path(ax, graph, path, color, linewidth, alpha=1.0):
    """Plot a given path on the graph."""
    for u, v in zip(path[:-1], path[1:]):
        if graph.has_edge(u, v):
            edge_data = graph.get_edge_data(u, v, 0)
            line = edge_data.get('geometry', LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])]))
            ax.plot(*line.xy, color=color, linewidth=linewidth, solid_capstyle='round', alpha=alpha)

def main(traffic_data_file):
    configure_osmnx()
    graph = ox.graph_from_point((13.795535, 100.707066), network_type="all", dist=5000)
    load_and_apply_traffic_data(graph, traffic_data_file)

    all_nodes = list(graph.nodes())
    start_node, end_node = random.sample(all_nodes, 2)
    # print(f"{start_node}:{end_node}")
    start_node, end_node = 7882881260,1696499108


    # Compare routes based on time and length including execution time
    find_and_plot_routes(graph, start_node, end_node, weight='length')

if __name__ == "__main__":
    traffic_data_file = "traffic_data_Monday_1.json"
    main(traffic_data_file)

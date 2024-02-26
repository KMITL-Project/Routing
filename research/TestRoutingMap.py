import os
import json
import time
import uuid
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
from geopy.distance import great_circle
import random

def configure_osmnx():
    """Configure OSMnx settings."""
    ox.config(use_cache=True)

def haversine_distance(u, v, graph):
    """Calculate the haversine distance between two nodes in a graph."""
    u_latlon = (graph.nodes[u]['y'], graph.nodes[u]['x'])
    v_latlon = (graph.nodes[v]['y'], graph.nodes[v]['x'])
    return great_circle(u_latlon, v_latlon).meters

def load_json_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def apply_traffic_data_to_graph(graph, traffic_data_path):
    """Apply traffic data to a graph from a specified JSON file."""
    traffic_data = load_json_data(traffic_data_path)

    for u, v, key, data in graph.edges(keys=True, data=True):
        edge_key = f"{u},{v}"
        if edge_key in traffic_data:
            data['time'] = traffic_data[edge_key]

def find_and_plot_routes(graph, start_node, end_node, heuristic, weight='time',image_name=""):
    """Find routes using A* and Dijkstra's algorithm, then plot, compare them, and calculate sum length."""
    # A* path finding
    start_time_astar = time.time()
    path_astar = nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight=weight)
    end_time_astar = time.time()
    length_astar = nx.path_weight(graph, path_astar, weight='length')
    time_use_astar = nx.path_weight(graph, path_astar, weight='time')

    # Dijkstra's shortest path
    start_time_dijkstra = time.time()
    # path_dijkstra = nx.shortest_path(graph,start_node, end_node, weight=weight)
    path_dijkstra = nx.dijkstra_path(graph,start_node, end_node, weight=weight)
    end_time_dijkstra = time.time()
    length_dijkstra = nx.path_weight(graph, path_dijkstra, weight='length')
    time_use_dijkstra = nx.path_weight(graph, path_dijkstra, weight='time')

    astar_execution = end_time_astar - start_time_astar
    dijkstra_execution = end_time_dijkstra - start_time_dijkstra

    print(f"Weight:{weight} ID: {image_name}")
    print(f"A*:{astar_execution:.4f}")
    print(f"D:{dijkstra_execution:.4f}")


    # Plotting
    fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=0)
    plot_path(ax, graph, path_astar, 'blue', 4)
    plot_path(ax, graph, path_dijkstra, 'red', 2, alpha=0.5)

    plt.savefig(f"./image_result/{image_name}_{weight}.png", bbox_inches='tight', dpi=700)

    log_message = f"image: {image_name}_{weight}\t\tStart Node: {start_node}, End Node: {end_node}, " \
                  f"A* Path Length: {len(path_astar)} nodes, Total Length: {length_astar:.2f} meters, execution time: {astar_execution:.4f} seconds, time use: {time_use_astar:.4f}\t\t" \
                  f"Dijkstra's Path Length: {len(path_dijkstra)} nodes, Total Length: {length_dijkstra:.2f} meters, execution time: {dijkstra_execution:.4f} seconds, time use: {time_use_dijkstra:.4f}\n"
    
    csv_row = f"{image_name},{weight},{start_node},{end_node},{len(path_astar)},{length_astar:.2f},{astar_execution:.4f},{time_use_astar:.4f},{len(path_dijkstra)},{length_dijkstra:.2f},{dijkstra_execution:.4f},{time_use_dijkstra:.4f}\n"
    log_results(csv_row)

def plot_path(ax, graph, path, color, linewidth, alpha=1.0):
    """Plot a given path on the graph."""
    for u, v in zip(path[:-1], path[1:]):
        if graph.has_edge(u, v):
            edge_data = graph.get_edge_data(u, v, 0)
            line = edge_data.get('geometry', LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])]))
            ax.plot(*line.xy, color=color, linewidth=linewidth, solid_capstyle='round', alpha=alpha)

def log_results(message):
    """Log results to a file."""
    with open("./image_result/log.csv", 'a') as log_file:
        log_file.write(message)

def main(traffic_data_file):
    configure_osmnx()
    graph = ox.graph_from_point((13.795535, 100.707066), network_type="all", dist=5000)
    apply_traffic_data_to_graph(graph, traffic_data_file)
   
    all_nodes = list(graph.nodes())
    start_node = random.choice(all_nodes)
    end_node = random.choice(all_nodes)

    heuristic = lambda u, v: haversine_distance(u, v, graph)

    image_name = str(uuid.uuid4())
    find_and_plot_routes(graph, start_node, end_node, heuristic, weight='time',image_name=image_name)
    find_and_plot_routes(graph, start_node, end_node, heuristic, weight='length',image_name=image_name)

if __name__ == "__main__":
    traffic_data_file = "traffic_data_Monday_1.json"
    log_results("image_name,weight,start_node,end_node,path_length_astar,total_length_astar_meters,execution_time_astar_seconds,time_use_astar,path_length_dijkstra,total_length_dijkstra_meters,execution_time_dijkstra_seconds,time_use_dijkstra\n")
    for i in range(0,6):
        main(traffic_data_file)

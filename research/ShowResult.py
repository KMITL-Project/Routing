import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
from geopy.distance import great_circle
import random
import uuid
import json
import time
import os

ox.config(use_cache=True)

def haversine(u, v, graph):
    u_latlon = (graph.nodes[u]['y'], graph.nodes[u]['x'])
    v_latlon = (graph.nodes[v]['y'], graph.nodes[v]['x'])
    return great_circle(u_latlon, v_latlon).meters

def load_traffic_data(traffic_data_file):
    try:
        with open(traffic_data_file, 'r') as file:
            return json.load(file)
    except IOError:
        print("Error opening or reading traffic data file")
        return {}

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
    """Plot a path on the graph."""
    for u, v in zip(path[:-1], path[1:]):
        if graph.has_edge(u, v):
            edge_data = graph.get_edge_data(u, v, 0)
            line = edge_data.get('geometry', LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])]))
            plt.plot(*line.xy, color=color, linewidth=linewidth, solid_capstyle='round', alpha=alpha)

def plot_path_with_edge_weights(graph, path, color, linewidth, alpha=1):
    """Plot a path on the graph and annotate each edge with its weight."""
    for u, v in zip(path[:-1], path[1:]):
        if graph.has_edge(u, v):
            edge_data = graph.get_edge_data(u, v, 0)
            line = edge_data.get('geometry', LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), 
                                                         Point(graph.nodes[v]['x'], graph.nodes[v]['y'])]))
            plt.plot(*line.xy, color=color, linewidth=linewidth, solid_capstyle='round', alpha=alpha)
            
            # Calculate the midpoint for the annotation
            if 'geometry' in edge_data:
                mid_point = line.interpolate(0.5, normalized=True)
            else:
                mid_x = (graph.nodes[u]['x'] + graph.nodes[v]['x']) / 2
                mid_y = (graph.nodes[u]['y'] + graph.nodes[v]['y']) / 2
                mid_point = Point(mid_x, mid_y)
            
            # Annotate edge with its weight
            plt.annotate(f"{edge_data['time']:.1f}", 
                         (mid_point.x, mid_point.y), 
                         textcoords="offset points", 
                         xytext=(0,5), 
                         ha='center', 
                         color=color)


def plot_path_with_heuristics(graph, path, end_node, color, linewidth):
    """Plot the A* path on the graph and annotate each node with its heuristic value."""
    for u in path[:-1]:  # Exclude the end node itself
        v = end_node
        heuristic_value = haversine(u, v, graph)
        if u in graph.nodes:
            x, y = graph.nodes[u]['x'], graph.nodes[u]['y']
            plt.scatter(x, y, color=color, s=10)  # Mark the node
            # Annotate the node with its heuristic value
            plt.text(x, y, f"{heuristic_value:.1f}", color=color, fontsize=9)

def plot_path_with_edge_weights_and_heuristics(graph, path, color, linewidth, alpha=1, annotate_heuristic=False, end_node=None):
    """Plot a path on the graph, annotate each edge with its weight, and optionally annotate nodes with heuristic values."""
    for u, v in zip(path[:-1], path[1:]):
        if graph.has_edge(u, v):
            edge_data = graph.get_edge_data(u, v, 0)
            line = edge_data.get('geometry', LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])]))
            plt.plot(*line.xy, color=color, linewidth=linewidth, solid_capstyle='round', alpha=alpha)
            
            # Annotate edge with its weight
            mid_point = line.interpolate(0.5, normalized=True)
            plt.text(mid_point.x, mid_point.y, f"{edge_data['time']:.1f}", color=color, fontsize=9)
    
    if annotate_heuristic and end_node:
        plot_path_with_heuristics(graph, path, end_node, 'green', linewidth)

def plot_surrounding_edges_with_weights(graph, path_a, path_b, ax, color='grey', alpha=0.5):
    """Plot edges around the A* and Dijkstra paths with their weights."""
    # Combine nodes from both paths to cover the surroundings of both
    nodes = set(path_a + path_b)
    plotted_edges = set()  # Keep track of plotted edges to avoid duplicates
    
    for node in nodes:
        # Iterate over all edges connected to the node
        for u, v, data in graph.edges(node, data=True):
            if (u, v) not in plotted_edges and (v, u) not in plotted_edges:  # Check if the edge has not been plotted yet
                if 'geometry' in data:
                    line = data['geometry']
                else:
                    line = LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), 
                                       Point(graph.nodes[v]['x'], graph.nodes[v]['y'])])
                
                # Plot the edge
                ax.plot(*line.xy, color=color, linewidth=1, alpha=alpha)
                
                # Annotate the edge with its weight, if 'time' is the weight attribute
                mid_point = line.interpolate(0.6, normalized=True)
                weight = data.get('time', 0)  # Replace 'time' with your actual weight attribute
                ax.text(mid_point.x, mid_point.y, f"W:{weight:.1f}", color=color, fontsize=9, ha='center')
                
                plotted_edges.add((u, v))  # Mark this edge as plotted

def plot_surrounding_edges_with_heuristics(graph, path_a, path_b, end_node, ax, color='grey', alpha=0.5):
    nodes = set(path_a + path_b)  # Combine nodes from both paths
    plotted_edges = set()  # Keep track of plotted edges to avoid duplicates
    
    for node in nodes:
        # Iterate over all edges connected to the node
        for u, v, data in graph.edges(node, data=True):
            if (u, v) not in plotted_edges and (v, u) not in plotted_edges:  # Check if the edge has not been plotted
                if 'geometry' in data:
                    line = data['geometry']
                else:
                    line = LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])])
                
                # Plot the edge
                ax.plot(*line.xy, color=color, linewidth=1, alpha=alpha)
                
                # Determine which node's heuristic to use (choose the one closer to the end node)
                heuristic_u = haversine(u, end_node, graph)
                heuristic_v = haversine(v, end_node, graph)
                heuristic_value = min(heuristic_u, heuristic_v)
                
                # Annotate the edge with the chosen heuristic value
                mid_point = line.interpolate(0.3, normalized=True)
                ax.text(mid_point.x,mid_point.y, f"H:{heuristic_value:.1f}", color=color, fontsize=9, ha='center', va='center')
                
                plotted_edges.add((u, v))  # Mark this edge as plotted

def plot_surrounding_edges_with_weights_and_heuristics(graph, path_a, path_b, end_node, ax, edge_color='grey', weight_color='black', heuristic_color='blue', alpha=0.5):
    """Plot edges around the A* and Dijkstra paths, annotating them with their weights and heuristic values."""
    nodes = set(path_a+path_b)  # Combine nodes from both paths
    plotted_edges = set()  # Keep track of plotted edges to avoid duplicates
    
    for node in nodes:
        for u, v, data in graph.edges(node, data=True):
            if (u, v) not in plotted_edges and (v, u) not in plotted_edges:
                if 'geometry' in data:
                    line = data['geometry']
                else:
                    line = LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])])
                
                # Plot the edge
                ax.plot(*line.xy, color=edge_color, linewidth=1, alpha=alpha)
    
                print(f"{graph.nodes[u]}:{u}|{graph.nodes[v]}:{v}")
                
                # Determine which node's heuristic to use (choose the one closer to the end node)
                heuristic_u = haversine(u, end_node, graph)
                heuristic_v = haversine(v, end_node, graph)
                heuristic_value = min(heuristic_u, heuristic_v)
                
                # Annotate the edge with its weight and heuristic value
                mid_point = line.interpolate(0.5, normalized=True)
                weight_text = f"W: {data.get('length', 0):.1f}"  # Replace 'time' with your weight attribute
                ax.text(mid_point.x, mid_point.y, weight_text, color=weight_color, fontsize=9, ha='center')
                
                mid_point = line.interpolate(0.1, normalized=True)
                heuristic_text = f"H: {heuristic_value:.1f}"
                ax.text(mid_point.x, mid_point.y, heuristic_text, color=heuristic_color, fontsize=9, ha='center')
                
                plotted_edges.add((u, v))

graph = ox.graph_from_point((13.795535, 100.707066), network_type="all", dist=5000)
traffic_data_path = "./traffic_data_Monday_1.json"
apply_traffic_data(graph, traffic_data_path) 

def heuristic(u, v):
        return haversine(u, v, graph)

# start_node = 2302314957
# end_node = 8034568525

start_node = 7950006901
# end_node = 3843779770
end_node = 3843779770


# ** original 
# start_node = 8038827842
# end_node = 8034568525

shortest_path_astar = nx.astar_path(graph, start_node, end_node, heuristic=heuristic, weight='time')
shortest_path_dijkstra = nx.shortest_path(graph, start_node, end_node, weight='time')

fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=10)



# plot_path(graph, shortest_path_astar, color="blue", linewidth=2, alpha=1)
# plot_path(graph, shortest_path_dijkstra, color="fuchsia", linewidth=4, alpha=0.5)

# plot_surrounding_edges_with_weights_and_heuristics(graph, shortest_path_astar, shortest_path_dijkstra, end_node, ax,edge_color='red', weight_color='green', heuristic_color='orange')


# plot_surrounding_edges_with_weights(graph, shortest_path_astar, shortest_path_dijkstra, ax,color='green')
# plot_surrounding_edges_with_heuristics(graph, shortest_path_astar, shortest_path_dijkstra, end_node, ax,color='orange')

# plot_path_with_edge_weights_and_heuristics(graph, shortest_path_astar, 'blue', 4, annotate_heuristic=True, end_node=end_node)
# plot_path_with_edge_weights_and_heuristics(graph, shortest_path_dijkstra, 'red', 2, alpha=0.5)

# for i in range(0,200):
#     if shortest_path_astar[i] != shortest_path_dijkstra[i] :
#         print(shortest_path_astar[i-1],shortest_path_dijkstra[i-1],end="\n")
#         break

plt.show()
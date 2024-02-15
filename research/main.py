import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import os
import json
from shapely.geometry import LineString, Point
from datetime import datetime
from matplotlib.cm import ScalarMappable

# Configure OSMnx
ox.config(use_cache=True, log_console=True)

def fetch_traffic_data_rand(graph, traffic_data_file):
    """
    Simulates fetching traffic data by generating random multipliers.
    """
    traffic_data = {}
    # Simulate time of day effect: Assuming 0 (midnight) to 23 (11 PM) hour format
    # current_hour = datetime.now().hour
    current_hour = 8
    # Determine a base multiplier based on time of day, simulating rush hour effects
    if 7 <= current_hour <= 9 or 16 <= current_hour <= 18:  # Typical rush hours
        base_multiplier = 1.5
    else:
        base_multiplier = 1.0

    for u, v, data in graph.edges(data=True):
        # Simulate road type effect: Major roads are more likely to have traffic
        road_type = data.get('highway', '')
        if road_type in ['motorway', 'primary', 'secondary']:
            road_multiplier = 1.2  # Higher multiplier for major roads
        else:
            road_multiplier = 1.0  # Lower multiplier for smaller roads

        # Combine base multiplier with road type effect and add some random variation
        traffic_multiplier = base_multiplier * road_multiplier * random.uniform(0.8, 1.2)

        traffic_data[f"{u},{v}"] = traffic_multiplier

    # Save simulated traffic data to file
    with open(traffic_data_file, 'w') as file:
        json.dump(traffic_data, file)
    
    return traffic_data

def load_traffic_data(cache_dir="traffic_data_Monday_8.json"):
    traffic_data = []
    with open(cache_dir) as file:
        traffic_data = json.load(file)
    return traffic_data

def load_and_aggregate_traffic_data(cache_dir, total_days, period):
    """
    Loads and aggregates traffic data from multiple days for a specific period.
    
    :param cache_dir: Directory where traffic data files are stored.
    :param total_days: Total number of days to include in the aggregation.
    :param period: The time period ('morning', 'noon', 'afternoon') to aggregate data for.
    :return: Aggregated traffic data, with average multipliers for each edge.
    """
    aggregated_data = {}
    count_data = {}

    for day in range(1, total_days + 1):
        filename = f"traffic_data_day{day}_{period}.json"
        filepath = os.path.join(cache_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                traffic_data = json.load(file)
            
            for edge, multiplier in traffic_data.items():
                if edge in aggregated_data:
                    aggregated_data[edge] += multiplier
                    count_data[edge] += 1
                else:
                    aggregated_data[edge] = multiplier
                    count_data[edge] = 1

    # Calculate average multiplier for each edge
    for edge in aggregated_data:
        aggregated_data[edge] /= count_data[edge]

    return aggregated_data

def apply_traffic_data(graph, traffic_data):
    """
    Applies the traffic data to modify edge lengths in the graph.
    """
    for u, v, key, data in graph.edges(keys=True, data=True):
        edge_key = f"{u},{v}"
        if edge_key in traffic_data:
            # data['length'] *= traffic_data[edge_key]
            print(traffic_data[edge_key])
            data['length'] = traffic_data[edge_key]

def calculate_travel_time(graph, path, traffic_data, avg_speed_km_per_hr=30):
    total_time_minutes = 0
    for u, v in zip(path[:-1], path[1:]):
        edge_data = graph.get_edge_data(u, v, 0)
        length_meters = edge_data['length']
        key = f"{u},{v}"
        traffic_multiplier = traffic_data.get(key, 1)
        # Adjust length for traffic multiplier
        adjusted_length_meters = length_meters * traffic_multiplier
        # Convert length to kilometers and speed to km/hr to get time in hours
        time_hours = adjusted_length_meters / 1000 / avg_speed_km_per_hr
        # Convert time to minutes
        total_time_minutes += time_hours * 60
    return total_time_minutes

def plot_route_with_traffic_mod(start_point, end_point, traffic_data_file):
    """
    Plots the route from start_point to end_point considering traffic data.
    """
    graph = ox.graph_from_point(start_point, network_type="all", dist=10000)
    # traffic_data = fetch_traffic_data_rand(graph, traffic_data_file)
    # traffic_data = load_and_aggregate_traffic_data("trafficData",2,"morning")
    traffic_data = load_traffic_data()
    apply_traffic_data(graph, traffic_data)

    # start_node = ox.distance.nearest_nodes(graph, start_point[1], start_point[0])
    # end_node = ox.distance.nearest_nodes(graph, end_point[1], end_point[0])
    all_nodes = list(graph.nodes())
    start_node = random.choice(all_nodes)
    end_node = random.choice(all_nodes)

    shortest_path = nx.shortest_path(graph, start_node, end_node, weight='length')
    total_time_minutes = calculate_travel_time(graph, shortest_path, traffic_data)

    print(f"Total travel time: {total_time_minutes:.2f} minutes")

    # Plot the graph
    fig, ax = ox.plot_graph(graph, show=False, close=False, node_size=0)

    # Create a color map and normalization based on traffic data
    cmap = plt.cm.viridis
    norm = mcolors.Normalize(vmin=0.5, vmax=100.0)

    # Plot each edge in the shortest path with color based on traffic multiplier
    for u, v in zip(shortest_path[:-1], shortest_path[1:]):
        key = f"{u},{v}"
        multiplier = traffic_data.get(key, 1)  # Default to 1 if key not found
        color = cmap(norm(multiplier))
        edge = graph[u][v][0]
        line = edge['geometry'] if 'geometry' in edge else LineString([Point(graph.nodes[u]['x'], graph.nodes[u]['y']), Point(graph.nodes[v]['x'], graph.nodes[v]['y'])])
        ax.plot(*line.xy, color=color, linewidth=6, solid_capstyle='round')

    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Traffic Multiplier',color='white')
    cbar.ax.yaxis.set_tick_params(color='white')  # For tick color
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')  # For tick label color

    plt.show()

# Example usage
start = (13.795359, 100.706923)  # Start latitude and longitude
end = (13.789273, 100.625812)    # End latitude and longitude
traffic_data_file = "traffic_data_Monday_8.json"

plot_route_with_traffic_mod(start, end, traffic_data_file)

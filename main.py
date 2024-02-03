import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import time

# Pre-define your origin/destination points
origin = (18.3154146, 99.3999579)
destination = (18.3135446, 99.3905726)

# Retrieve and simplify the OSM network graph
G = ox.graph_from_point(origin, network_type="all", dist=2000, simplify=True)

# Add edge lengths and speed limits (replace with actual data) to the graph for weight calculations
G = ox.distance.add_edge_lengths(G)
G = ox.speed.add_edge_speeds(G, hwy_speeds={"motorway": 100, "trunk": 80, "primary": 60, "secondary": 50, "tertiary": 40, "residential": 30, "unclassified": 20})

# Generate random traffic factors for each edge (replace with real data)
# Here, we generate random traffic factors between 0 and 1 for all edges
traffic_data = {
    (u, v, k): random.uniform(0, 1)
    for u, v, k, data in G.edges(keys=True, data=True)
}

# Calculate edge weights based on length, speed limits, and traffic
max_length = max(data['length'] for _, _, _, data in G.edges(keys=True, data=True))
edge_weights = [
    (data['length'] / max_length) * (1 / data['speed_kph']) * traffic_data.get((u, v, k), 1.0)
    for u, v, k, data in G.edges(keys=True, data=True)
]

# Create a colormap based on edge weights
cmap = plt.cm.viridis

# Normalize the edge weights for coloring
min_weight = min(edge_weights)
max_weight = max(edge_weights)
norm = plt.Normalize(vmin=min_weight, vmax=max_weight)

# Calculate edge colors based on weight
edge_colors = [cmap(norm(w)) for w in edge_weights]

# Generate random destination and source nodes
all_nodes = list(G.nodes())
source_node = random.choice(all_nodes)
target_node = random.choice(all_nodes)

# Check if there is a path between the source and target nodes
if not nx.has_path(G, source=source_node, target=target_node):
    print("No path found between source and target nodes.")
else:
    # Calculate the shortest path using the A* algorithm with the random nodes
    shortest_path = nx.astar_path(G, source=source_node, target=target_node, heuristic=None, weight="length")

    # Calculate estimated travel time (in hours) based on the selected path
    estimated_travel_time_hours = sum(
        G.edges[u, v, 0]['length'] / (G.edges[u, v, 0]['speed_kph'] * 1000 / 3600)
        for u, v in zip(shortest_path[:-1], shortest_path[1:])
    )

    travel_distance_km = sum(G.edges[u, v, 0]['length'] / 1000 for u, v in zip(shortest_path[:-1], shortest_path[1:]))
    print(travel_distance_km)
    # Print the estimated travel time
    print(f"Estimated travel time from source to destination: {estimated_travel_time_hours:.2f} hours")

    # Plot the graph with edge colors based on weight
    fig, ax = ox.plot_graph(
        G,
        bgcolor='k',
        edge_color=edge_colors,
        node_size=0,
        edge_linewidth=1.5,
        show=False
    )

    # Highlight the shortest path with a different color
    ox.plot_graph_route(G, shortest_path, route_color='red', route_linewidth=3, ax=ax)

    plt.show()
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Define the list of destinations (latitude, longitude)
destinations = [
    (13.795359, 100.706923),  # San Francisco
    (13.7978423,100.7051229),  # Los Angeles
    (13.782725, 100.700628),   # New York City
]

# Download the street network for a specific location (you can adjust the location and the network type as needed)
graph = ox.graph_from_point(destinations[0], network_type="all", dist=5000)

# Create a graph connecting all destinations with the street network
for dest in destinations:
    nearest_node = ox.distance.nearest_nodes(graph, dest[0], dest[1])
    graph = nx.compose(graph, nx.ego_graph(graph, nearest_node, radius=1000))

# Calculate the shortest path passing through all destinations
shortest_path = nx.approximation.traveling_salesman_problem(graph, heuristic_method="greedy")

# Plot the map with the shortest path
fig, ax = ox.plot_graph_route(graph, shortest_path, route_color='r', route_linewidth=6, node_size=0, bgcolor='k')

# Show the plot
plt.show()

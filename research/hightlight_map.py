import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random

# Pre-define your origin/destination points
origin = (18.3154146, 99.3999579)
destination = (18.3135446, 99.3905726)

# Retrieve and simplify the OSM network graph
G = ox.graph_from_point(origin, network_type="all", dist=2000, simplify=True)

# Add edge lengths to the graph for weight calculations
G = ox.distance.add_edge_lengths(G)

# Simulate hypothetical traffic data (replace with real data)
# Here, we create a dictionary where keys are edges and values are traffic factors
# You should replace this with real traffic data or API calls
traffic_data = {
    (u, v, k): random.uniform(0.1, 1.0)
      for u, v, k, data in G.edges(keys=True, data=True)
}

# Calculate edge weights based on length and traffic
max_length = max(data['length'] for _, _, _, data in G.edges(keys=True, data=True))
edge_weights = [
    (data['length'] / max_length) * traffic_data.get((u, v, k), 1.0)
    for u, v, k, data in G.edges(keys=True, data=True)
]

# Create a colormap based on edge weights
cmap = plt.cm.viridis
norm = mcolors.Normalize(vmin=0, vmax=2.0)  # Assuming traffic factors range from 0.1 to 2.0

# Calculate edge colors based on weight
edge_colors = [cmap(norm(w)) for w in edge_weights]

# Plot the graph with edge colors based on weight
fig, ax = ox.plot_graph(G, bgcolor='k', edge_color=edge_colors, node_size=0, edge_linewidth=1.5, show=False)

# Create a colorbar for the edge colors
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label('Edge Weight', fontsize=12)

plt.show()
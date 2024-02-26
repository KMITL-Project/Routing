import networkx as nx
import numpy as np
import time
import matplotlib.pyplot as plt

# Function to generate a weighted graph
def generate_weighted_graph(n_nodes, seed=None):
    np.random.seed(seed)  # Optional seed for reproducibility
    G = nx.random_geometric_graph(n_nodes, 0.3)
    for (u, v) in G.edges():
        G.edges[u, v]['weight'] = np.random.rand()  # Assign random weights
    return G

# Function to measure execution time of shortest path computations
def measure_execution_time(G, source, target):
    # Measure nx.shortest_path with Dijkstra's method
    start = time.time()
    nx.shortest_path(G, source=source, target=target, method='dijkstra', weight='weight')
    shortest_path_time = time.time() - start

    # Measure nx.dijkstra_path
    start = time.time()
    nx.dijkstra_path(G, source=source, target=target, weight='weight')
    dijkstra_path_time = time.time() - start

    return shortest_path_time, dijkstra_path_time

# Generate a weighted graph
G = generate_weighted_graph(500, seed=42)

# Choose source and target nodes
source, target = 0, 499

# Measure execution times
shortest_path_time, dijkstra_path_time = measure_execution_time(G, source, target)

# Print results
print(f"nx.shortest_path (Dijkstra's method) execution time: {shortest_path_time:.5f} seconds")
print(f"nx.dijkstra_path execution time: {dijkstra_path_time:.5f} seconds")

# Plot the results
methods = ['nx.shortest_path\n(Dijkstra\'s method)', 'nx.dijkstra_path']
times = [shortest_path_time, dijkstra_path_time]

plt.figure(figsize=(8, 6))
plt.bar(methods, times, color=['blue', 'orange'])
plt.title('Execution Time Comparison')
plt.ylabel('Time (seconds)')
plt.show()

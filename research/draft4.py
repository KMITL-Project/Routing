import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import googlemaps
from geopy.distance import great_circle

# Set up Google Maps API client
gmaps = googlemaps.Client(key='AIzaSyCPFkLO3IXNYOExwH-2JUnafyjWHURr4U8')

# Define your origin and destination points
origin = (18.3154146,99.3999579)
destination = (18.3135446,99.3905726)

# Retrieve the OSM network graph for a specific area
G = ox.graph_from_point(origin, network_type="all", dist=2000)

# Convert the network graph to a NetworkX graph
G_nx = nx.Graph(G)

# Define the A* heuristic function
def heuristic(node, destination):
    return great_circle(node, destination).meters

# Fetch real-time traffic data using Google Maps Distance Matrix API
def get_traffic_weight(u, v):
    print(u,v)
    # Convert latitude and longitude to addresses
    # origin_address = gmaps.reverse_geocode(origin)[0]['formatted_address']
    # destination_address = gmaps.reverse_geocode(destination)[0]['formatted_address']

    # # Request traffic data using the Distance Matrix API
    # result = gmaps.distance_matrix(
    #     origin_address,
    #     destination_address,
    #     mode="driving",
    #     traffic_model="best_guess",  # You can use "best_guess" or "pessimistic" for traffic estimation
    #     departure_time="now"  # Specify the current time for real-time data
    # )

    # # Extract the duration in traffic and convert it to meters (or other units)
    # traffic_duration = result['rows'][0]['elements'][0]['duration_in_traffic']['value']
    # print(traffic_duration)
    # traffic_duration_meters = traffic_duration / 60 * 1000  # Convert to meters

    # return traffic_duration_meters
    return 10

# Assign traffic-based edge weights
for u, v, data in G_nx.edges(data=True):
    data['weight'] = get_traffic_weight((data['osmid'], u), (data['osmid'], v))

# Find the shortest path using A* with traffic-based weights
shortest_path = nx.astar_path(G_nx, origin, destination, heuristic=heuristic, weight="weight")

# Plot the OSM network graph with the shortest path
fig, ax = ox.plot_graph(ox.project_graph(G_nx), show=False, close=False)

# Extract coordinates from the shortest path
shortest_path_coordinates = list(map(tuple, ox.graph_to_gdfs(G_nx, nodes=False).loc[shortest_path].geometry.values))

# Plot the shortest path
x, y = zip(*shortest_path_coordinates)
ax.plot(x, y, 'r', linewidth=3)

# Show the plot
plt.show()
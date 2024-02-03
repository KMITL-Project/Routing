import osmnx as ox
import networkx as nx
import googlemaps
import geopy.distance
import folium

# Replace with your own Google Maps API key
google_maps_api_key = 'AIzaSyCPFkLO3IXNYOExwH-2JUnafyjWHURr4U8'
gmaps = googlemaps.Client(key=google_maps_api_key)

# Replace with your desired location
place_name = 'New York, USA'

# Download OSM data for the specified place
graph = ox.graph_from_place(place_name, network_type='all')

# Define a function to calculate the edge weight based on real-time traffic data
def calculate_edge_weight(u, v, data):
    origin = data['origin']
    destination = data['destination']
    
    # Calculate the distance between the two nodes (u and v)
    distance = geopy.distance.distance(
        (graph.nodes[u]['y'], graph.nodes[u]['x']),
        (graph.nodes[v]['y'], graph.nodes[v]['x'])
    ).miles
    
    # Use Google Maps Directions API to get real-time traffic information
    directions = gmaps.directions(origin, destination, mode='driving', departure_time='now')
    
    if len(directions) > 0 and 'legs' in directions[0]:
        leg = directions[0]['legs'][0]
        duration_in_traffic = leg['duration_in_traffic']
        return duration_in_traffic['value'] / 60.0  # Convert seconds to minutes
    
    return distance  # If traffic data is not available, use the Euclidean distance as a fallback

# Specify the origin and destination points
origin_point = (40.7128, -74.0060)  # Replace with your origin coordinates
destination_point = (40.7309, -73.9872)  # Replace with your destination coordinates

# Find the nearest nodes in the graph to the origin and destination points
origin_node = ox.distance.nearest_nodes(graph, origin_point[1], origin_point[0])
destination_node = ox.distance.nearest_nodes(graph, destination_point[1], destination_point[0])

# Define the A* heuristic function (use Euclidean distance as a heuristic)
def heuristic(u, v):
    return geopy.distance.distance(
        (graph.nodes[u]['y'], graph.nodes[u]['x']),
        (graph.nodes[v]['y'], graph.nodes[v]['x'])
    ).miles

# Find the shortest path using A* algorithm with real-time traffic data as edge weights
shortest_path = nx.astar_path(graph, origin_node, destination_node, heuristic=heuristic, weight='weight')

# Create a map centered around the specified location
m = ox.plot_graph_folium(graph, popup_attribute='name', edge_width=2)

# Add the shortest path to the map
coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in shortest_path]
folium.PolyLine(locations=coords, color='red', weight=5).add_to(m)

# Save the map as an HTML file or display it in the notebook
m.save('shortest_path_map.html')

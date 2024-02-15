import googlemaps
from datetime import datetime
import osmnx as ox
import matplotlib.pyplot as plt
import json

# Initialize Google Maps client with your API key
api_key = 'AIzaSyCPFkLO3IXNYOExwH-2JUnafyjWHURr4U8'
gmaps = googlemaps.Client(key=api_key)

def get_google_maps_route(start, end, gmaps_client):
    """Fetch route from Google Maps."""
    directions_result = gmaps_client.directions(start, end, mode="driving", departure_time=datetime.now())
    return directions_result

def save_directions_to_json(directions_result, filename='directions_result.json'):
    """Save directions result to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(directions_result, file, indent=4)

def extract_lat_lng_from_directions_result(directions_result):
    """Extract latitude and longitude points from directions result."""
    lat_lng_points = []
    for leg in directions_result[0]['legs']:
        for step in leg['steps']:
            start_location = step['start_location']
            end_location = step['end_location']
            lat_lng_points.append((start_location['lat'], start_location['lng']))
            lat_lng_points.append((end_location['lat'], end_location['lng']))
    return lat_lng_points

def plot_google_maps_route_on_osm(lat_lng_points):
    """Plot a route on an OSM map."""
    if not lat_lng_points:
        print("No points to plot.")
        return

    # Assuming the first point is central enough for the map
    G = ox.graph_from_point(lat_lng_points[0], dist=3000, network_type='drive')
    fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='gray', node_size=0)

    # Convert lat and lng to x and y for plotting
    xs, ys = zip(*[(lng, lat) for lat, lng in lat_lng_points])

    # Plot the route
    ax.plot(xs, ys, marker='o', color='red', markersize=5, linestyle='-', linewidth=2, alpha=0.7)

    plt.show()

# Example usage
start_address = 'Central Park, New York, NY'
end_address = 'Times Square, New York, NY'

# Fetch route from Google Maps
directions_result = get_google_maps_route(start_address, end_address, gmaps)

# Save the fetched directions to a JSON file
save_directions_to_json(directions_result)

# Extract lat-lng points from directions result
lat_lng_points = extract_lat_lng_from_directions_result(directions_result)

# Plot the Google Maps route on an OSM map
plot_google_maps_route_on_osm(lat_lng_points)

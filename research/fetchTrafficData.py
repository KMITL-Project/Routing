import os
import json
import datetime 
import googlemaps

def fetch_traffic_data(graph, api_key, traffic_data_file):
    # Check if recent traffic data file exists
    if os.path.exists(traffic_data_file):
        print("Cache traffic data exists.")
        with open(traffic_data_file, 'r') as file:
            traffic_data = json.load(file)
        return traffic_data

    print("Cache traffic data does not exist.")
    gmaps = googlemaps.Client(key=api_key)
    traffic_data = {}
    count = 0
    for u, v, data in graph.edges(data=True):
        try:
            start_point = graph.nodes[u]
            end_point = graph.nodes[v]
            start_latlng = (start_point['y'], start_point['x'])
            end_latlng = (end_point['y'], end_point['x'])
            directions_result = gmaps.directions(start_latlng,
                                                 end_latlng,
                                                 mode="driving",
                                                 departure_time=datetime.datetime.now(),
                                                 traffic_model="best_guess")
            duration_in_traffic = directions_result[0]['legs'][0]['duration_in_traffic']['value']
            base_duration = directions_result[0]['legs'][0]['duration']['value']
            traffic_multiplier = duration_in_traffic / base_duration if base_duration > 0 else 1
            traffic_data[f"{u},{v}"] = traffic_multiplier
            count += 1
            print("Fetched direction API", count)
        except Exception as e:
            print(f"Error fetching traffic data for edge {u},{v}: {e}")
            # traffic_data[f"{u},{v}"] = 1

    # Save traffic data to file
    with open(traffic_data_file, 'w') as file:
        json.dump(traffic_data, file)
    
    return traffic_data


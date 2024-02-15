import os
import json
import datetime 
import googlemaps

class traffic_data:
    cache_path = "./cache_traffic/"

    def __init__(self,graph, api_key,path_file="default.json",cache=True ) -> None:
        self.graph = graph
        self.api_key = api_key
        self.path_file = self.cache_path+path_file
        self.cache = cache

    def fetch_traffic_data(self):
        # Check if recent traffic data file exists
        if self.cache and os.path.exists(self.path_file):
            print("Cache traffic data exists.")
            with open(self.path_file, 'r') as file:
                traffic_data = json.load(file)
            return traffic_data

        print("Cache traffic data does not exist.")
        gmaps = googlemaps.Client(key=self.api_key)
        traffic_data = {}
        count = 0
        for u, v, data in self.graph.edges(data=True):
            try:
                start_point = self.graph.nodes[u]
                end_point = self.graph.nodes[v]
                start_latlng = (start_point['y'], start_point['x'])
                end_latlng = (end_point['y'], end_point['x'])
                directions_result = gmaps.directions(start_latlng,
                                                     end_latlng,
                                                     mode="driving",
                                                     departure_time=datetime.datetime.now(),
                                                     traffic_model="best_guess")
                # directions_result = 1
                traffic_data[f"{u},{v}"] = directions_result[0]['legs'][0]['duration_in_traffic']['value']
                count += 1
                print("Fetched direction API", count)
            except Exception as e:
                print(f"Error fetching traffic data for edge {u},{v}: {e}")
                traffic_data[f"{u},{v}"] = 1  # Default to no traffic multiplier in case of error

        # Save traffic data to file
        with open(self.path_file, 'w') as file:
            json.dump(traffic_data, file)
        
        return traffic_data
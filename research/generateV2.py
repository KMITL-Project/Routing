import os
import json
import random
import osmnx as ox
from datetime import datetime, timedelta

# Configure OSMnx
ox.config(use_cache=True, log_console=True)

def calculate_base_travel_times(graph):
    """
    Calculates the base travel time in seconds for each edge in the graph,
    assuming default speed limits based on road type if not explicitly provided.
    """
    for u, v, data in graph.edges(data=True):
        speed_limit = data.get('maxspeed', 30)  # Default to 30 km/h if not specified
        if isinstance(speed_limit, list):  # Handle cases where maxspeed is a list
            speed_limit = min([int(s) for s in speed_limit if s.isdigit()], default=30)
        elif isinstance(speed_limit, str) and speed_limit.isdigit():
            speed_limit = int(speed_limit)
        else:
            speed_limit = 30  # Default if not a digit or if unspecified
        length_in_km = data['length'] / 1000  # Convert length from meters to kilometers
        data['base_travel_time'] = (length_in_km / speed_limit) * 3600  # Calculate travel time in seconds

def fetch_traffic_data_realistic(graph, current_hour, day_of_week):
    """
    Generates more realistic traffic multipliers, considering time of day, day of the week, and road type.
    """
    traffic_data = {}
    # Time of day adjustments
    if 7 <= current_hour <= 9:
        base_multiplier = random.uniform(1.4, 1.6)
    elif 12 <= current_hour <= 14:
        base_multiplier = random.uniform(1.1, 1.3)
    elif 16 <= current_hour <= 18:
        base_multiplier = random.uniform(1.4, 1.6)
    else:
        base_multiplier = random.uniform(0.9, 1.1)

    # Weekend adjustment
    weekend_adjustment = 0.8 if day_of_week in ['Saturday', 'Sunday'] else 1.0

    for u, v, data in graph.edges(data=True):
        # Road type adjustments
        road_type = data.get('highway', '')
        if road_type in ['motorway', 'trunk']:
            road_multiplier = random.uniform(1.2, 1.4)
        elif road_type in ['primary', 'secondary']:
            road_multiplier = random.uniform(1.1, 1.2)
        else:
            road_multiplier = random.uniform(1.0, 1.1)

        # Calculate traffic multiplier
        traffic_multiplier = base_multiplier * road_multiplier * weekend_adjustment
        traffic_data[f"{u},{v}"] = data['base_travel_time'] * traffic_multiplier  # Adjusted travel time in seconds
    return traffic_data

def save_traffic_data_to_file(data, filename):
    """
    Saves the traffic data to a JSON file.
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
location_point = (13.795359, 100.706923)
graph = ox.graph_from_point((13.795535, 100.707066), network_type="all", dist=5000)
calculate_base_travel_times(graph)

starting_date = datetime(2024, 1, 1)

time_periods = {
    '6:00': 6, 
    '7:00': 7,
    '8:00': 8,
    '11:00': 11, 
    '12:00': 12, 
    '13:00': 13, 
    '15:00': 15,
    '16:00': 16,
    '17:00': 17,
}

for day in range(1, 21):  # 20 days
    date = starting_date + timedelta(days=day-1)
    day_name = date.strftime("%A")  
    for period, hour in time_periods.items():
        print(day_name,period,hour)
        adjusted_travel_times = fetch_traffic_data_realistic(graph, hour, day_name)
        filename = f"./traffic_data/traffic_data_{day}_{day_name}_{period}.json"
        save_traffic_data_to_file(adjusted_travel_times, filename)
        print(f"Traffic data saved to {filename}.")
        
# # Simulate for a specific day and time
# day_of_week = "Monday"
# current_hour = 1
# adjusted_travel_times = fetch_traffic_data_realistic(graph, current_hour, day_of_week)

# # Save the generated traffic data to a file
# filename = f"traffic_data_{day_of_week}_{current_hour}.json"
# save_traffic_data_to_file(adjusted_travel_times, filename)
# print(f"Traffic data saved to {filename}.")

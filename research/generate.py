import os
import json
import random
import osmnx as ox
from datetime import datetime, timedelta

# Ensure OSMnx is configured to use the cache
ox.config(use_cache=True, log_console=True)

def fetch_traffic_data_rand(graph, traffic_data_file, current_hour):
    """
    Generates random traffic multipliers, simulating different times of the day.
    """
    traffic_data = {}
    # Determine base multiplier based on the simulated time of the day
    if 7 <= current_hour <= 9:  # Morning rush hour
        base_multiplier = 1.5
    elif 12 <= current_hour <= 14:  # Noon
        base_multiplier = 1.2
    elif 16 <= current_hour <= 18:  # Afternoon rush hour
        base_multiplier = 1.5
    else:
        base_multiplier = 1.0  # Default for other times

    for u, v, data in graph.edges(data=True):
        road_type = data.get('highway', '')
        road_multiplier = 1.2 if road_type in ['motorway', 'primary', 'secondary'] else 1.0
        traffic_multiplier = base_multiplier * road_multiplier * random.uniform(0.8, 1.2)
        traffic_data[f"{u},{v}"] = traffic_multiplier

    with open(traffic_data_file, 'w') as file:
        json.dump(traffic_data, file)

cache_dir = "trafficData"
os.makedirs(cache_dir, exist_ok=True)

# Load or create your graph here, for example:
location_point = (13.795359, 100.706923)
graph = ox.graph_from_point(location_point, network_type="all", dist=10000)

# Assuming a fixed starting date for day 1, for example, 2024-01-01
starting_date = datetime(2024, 1, 1)

# Time periods to simulate
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

# Generate and save traffic data for each period over 20 days
for day in range(1, 15):  # 20 days
    date = starting_date + timedelta(days=day-1)
    day_name = date.strftime("%A")  # Gets the name of the day
    for period, hour in time_periods.items():
        filename = f"{day_name}_day{day}_{period}.json"
        filepath = os.path.join(cache_dir, filename)
        fetch_traffic_data_rand(graph, filepath, current_hour=hour)
        print(f"Generated traffic data for {day_name} {period} of day {day}, saved to {filepath}.")

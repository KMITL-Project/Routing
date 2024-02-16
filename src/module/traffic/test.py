from fetch_traffic import TrafficData
import osmnx as ox


G = ox.graph_from_point((13.754739,100.7844444), network_type="all", dist=1000)

traffic = TrafficData(G,"AIzaSyD5TBRj94-U_Lg7IysPwwOv6FEdOOaBBwI","test.json")
print(len(traffic.fetch_traffic_data()))
from find_routing_multiple import Routing
import osmnx as ox

destinations = [
    (13.754739,100.7844444), 
    (13.75308, 100.79107),
    (13.75296,100.78015),
]

router = Routing(destinations[0])
router.apply_traffic_data("cache_traffic/test.json")
(best_path,best_length_meter,best_time_sec) = router.find_routing(destinations=destinations)
print(best_time_sec,best_length_meter)

router.plot_graph(best_path)


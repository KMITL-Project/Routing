from find_routing_multiple import Routing
import osmnx as ox

destinations = [
    (13.754739,100.7844444), 
    (13.75308, 100.79107),
    (13.75296,100.78015),
    (13.767088, 100.791784),
    (13.760834, 100.776447)
]

router = Routing(destinations[0],dist=5000,algorithm=Routing.AStart)
router.apply_traffic_data("cache_traffic/real-response-form-google.json")
(route_coords,best_path,best_length_meter,best_time_sec) = router.find_routing(destinations=destinations)
print("Time:",best_time_sec/60,"KM:",best_length_meter/1000)

router.plot_graph(best_path)


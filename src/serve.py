from flask import Flask, jsonify,request
from module.routing.find_routing_multiple import Routing

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Algitech API'})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'UP'})

@app.route('/get_route', methods=['POST'])
def get_route():
    # Assuming you have instantiated Routing class and graph
    latitudes = list(map(float, request.form.get('latitude').split(',')))
    longitudes = list(map(float, request.form.get('longitude').split(',')))

    destinations = list(zip(latitudes, longitudes))

    destinations = [(float(lat), float(lon)) for lat, lon in zip(latitudes, longitudes)]
    router = Routing(destinations[0])
    router.apply_traffic_data("cache_traffic/real-response-form-google.json")
    best_path,best_length_meter,best_time_sec, = router.find_routing(destinations)
    return jsonify({'route_coords': best_path, 'route_length': best_length_meter,'route_time':best_time_sec})


if __name__ == '__main__':
    app.run(debug=True,port=5000,host="0.0.0.0")

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
    try: 
        # Assuming you have instantiated Routing class and graph
        latitudes = list(map(float, request.form.get('latitude').split(',')))
        longitudes = list(map(float, request.form.get('longitude').split(',')))

        destinations = list(zip(latitudes, longitudes))

        router = Routing(destinations,dist=0)
        router.apply_traffic_data("cache_traffic/real-response-form-google.json")
        route_coords,best_path,best_length_meter,best_time_sec, = router.find_routing()
        return jsonify({'route_coords': route_coords, 'route_length': best_length_meter,'route_time':best_time_sec})
    except Exception as error:
        return jsonify({'code': 500,'message': str(error)})

if __name__ == '__main__':
    app.run(debug=True,port=5001,host="0.0.0.0")

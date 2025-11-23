from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import os
from utils import process_drawn_zone

app = Flask(__name__, static_folder='assets')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return send_file('bucharest_dual_map.html')

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_file(os.path.join('assets', path))

@app.route('/analyze', methods=['POST'])
def analyze_zone():
    try:
        data = request.json
        geometry = data.get('geometry')
        
        if not geometry:
            return jsonify({'error': 'No geometry provided'}), 400
            
        # Extract coordinates from GeoJSON Polygon
        # GeoJSON Polygon coords are nested: [[[lng, lat], ...]]
        # We need the outer ring: [[lng, lat], ...]
        if geometry['type'] == 'Polygon':
            coordinates = geometry['coordinates'][0]
        elif geometry['type'] == 'Rectangle': # Leaflet sometimes sends this?
             coordinates = geometry['coordinates'][0]
        else:
             # Fallback for other shapes if needed, or error
             return jsonify({'error': 'Unsupported geometry type'}), 400

        print(f"Received analysis request for polygon with {len(coordinates)} points")
        
        # Process with OSMnx
        results = process_drawn_zone(coordinates)
        
        return jsonify({'streets': results})
        
    except Exception as e:
        print(f"Error in analyze_zone: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Bucharest Map Server...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)

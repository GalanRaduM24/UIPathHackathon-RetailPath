from flask import Flask, send_file, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Get the base directory (parent of src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add backend to path
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend', 'services'))

from services.utils import process_drawn_zone

# Configure Flask to serve React app
FRONTEND_DIST = os.path.join(BASE_DIR, 'frontend', 'dist')
FRONTEND_OLD = os.path.join(BASE_DIR, 'frontend_old', 'templates')

app = Flask(__name__, 
            static_folder=FRONTEND_DIST,
            static_url_path='')
CORS(app)  # Enable CORS for all routes

# API Routes - MUST be defined before catch-all routes
@app.route('/api/analyze', methods=['POST'])
@app.route('/analyze', methods=['POST'])  # Also handle requests from embedded map
def analyze_zone():
    """Analyze a drawn zone and return street data"""
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/map-data', methods=['GET'])
def get_map_data():
    """Serve the old Bucharest map HTML for embedding"""
    try:
        map_path = os.path.join(FRONTEND_OLD, 'bucharest_dual_map.html')
        if os.path.exists(map_path):
            return send_file(map_path)
        else:
            return jsonify({'error': 'Map data not found'}), 404
    except Exception as e:
        print(f"Error serving map data: {e}")
        return jsonify({'error': str(e)}), 500

# React App Routes - Catch-all routes MUST be last
@app.route('/')
def serve_react_app():
    """Serve the React app index.html"""
    if os.path.exists(os.path.join(FRONTEND_DIST, 'index.html')):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    else:
        # Fallback to old map during development
        return send_file(os.path.join(FRONTEND_OLD, 'bucharest_dual_map.html'))

@app.route('/<path:path>')
def serve_react_routes(path):
    """Serve React app for all non-API routes"""
    # Check if it's a static file
    if os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    # Otherwise serve index.html for React Router
    elif os.path.exists(os.path.join(FRONTEND_DIST, 'index.html')):
        return send_from_directory(FRONTEND_DIST, 'index.html')
    else:
        return send_file(os.path.join(FRONTEND_OLD, 'bucharest_dual_map.html'))

if __name__ == '__main__':
    print("Starting RetailPath Server...")
    print("Frontend: http://127.0.0.1:5001")
    print("API: http://127.0.0.1:5001/api")
    print("\nFor development:")
    print("  1. Run this Flask server (port 5001)")
    print("  2. Run 'npm run dev' in frontend/ (port 5173)")
    print("  3. Open http://localhost:5173")
    app.run(debug=True, port=5001)

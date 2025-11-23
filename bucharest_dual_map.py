import folium
from folium.plugins import HeatMapWithTime, Draw
import branca.colormap as cm
import geopandas as gpd
import requests
import os
import json
from shapely.geometry import box, shape, Point
import sys
from dotenv import load_dotenv
import osmnx as ox
import warnings
warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
API_KEY_PRIVATE = os.getenv("BESTTIME_API_KEY")
KONTUR_FILE = "kontur_population_20231101.gpkg"
CACHED_POPULATION_FILE = "bucharest_population_hexagons.geojson"
NEIGHBORHOODS_FILE = "neighborghoods/bucharest_neighborhoods_final.geojson"

# Bucharest Bounding Box (approximate)
# [minx, miny, maxx, maxy]
BBOX_COORDS = [25.90, 44.33, 26.25, 44.55]

# Map Center
LAT = 44.4268
LNG = 26.1025

# BestTime API Config
BASE_URL = "https://besttime.app/api/v1/venues/filter"
RADIUS = 10000  # 10km
TYPES = 'BAR,RESTAURANT,CAFE,SHOPPING,PARK'
LIMIT = 500

def format_ranges(numbers):
    """
    Format a list of house numbers into ranges with gaps detection.
    Gaps > 20 create separate ranges.
    Example: [1, 2, 3, 50, 51, 52] -> "1-3, 50-52"
    """
    if not numbers:
        return ""
    
    # Convert to integers and sort
    nums = sorted([int(n) for n in numbers if str(n).isdigit()])
    
    if not nums:
        return ""
    
    if len(nums) == 1:
        return str(nums[0])
    
    ranges = []
    start = nums[0]
    prev = nums[0]
    
    for i in range(1, len(nums)):
        current = nums[i]
        
        # Gap detection: if gap > 20, close current range and start new one
        if current - prev > 20:
            # Close previous range
            if prev == start:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            # Start new range
            start = current
        
        prev = current
    
    # Close final range
    if prev == start:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")
    
    return ", ".join(ranges)

def process_drawn_zone(polygon_coords):
    """
    Extract streets and house numbers from a drawn polygon using OSMnx.
    
    Args:
        polygon_coords: List of [lng, lat] coordinates defining the polygon
    
    Returns:
        List of formatted street strings with house number ranges
    """
    try:
        print("\n=== Processing Drawn Zone ===")
        
        # Create shapely Polygon from coordinates
        # Convert from [lng, lat] to proper polygon
        from shapely.geometry import Polygon
        poly = Polygon(polygon_coords)
        
        print(f"Polygon bounds: {poly.bounds}")
        
        # Fetch street graph from polygon
        print("Fetching street network from OpenStreetMap...")
        try:
            G = ox.graph_from_polygon(poly, network_type='all')
            print(f"Retrieved {len(G.nodes)} nodes and {len(G.edges)} edges")
        except Exception as e:
            print(f"Warning: Could not fetch street graph: {e}")
            G = None
        
        # Fetch address nodes with house numbers
        print("Fetching address data...")
        try:
            tags = {'addr:housenumber': True}
            addresses = ox.features_from_polygon(poly, tags=tags)
            print(f"Retrieved {len(addresses)} address points")
        except Exception as e:
            print(f"Warning: Could not fetch addresses: {e}")
            addresses = None
        
        if addresses is None or addresses.empty:
            print("No addresses found in this area")
            return ["No addresses found in selected area"]
        
        # Group addresses by street
        street_data = {}
        
        for idx, row in addresses.iterrows():
            # Get street name
            street = row.get('addr:street', 'Unknown Street')
            housenumber = row.get('addr:housenumber', None)
            
            if housenumber and street:
                if street not in street_data:
                    street_data[street] = []
                
                # Extract numeric part of house number
                # Handle formats like "10A", "10-12", etc.
                num_str = ''.join(filter(str.isdigit, str(housenumber)))
                if num_str:
                    street_data[street].append(num_str)
        
        # Format results
        results = []
        for street, numbers in sorted(street_data.items()):
            if numbers:
                range_str = format_ranges(numbers)
                results.append(f"{street} ({range_str})")
            else:
                results.append(street)
        
        print(f"Found {len(results)} streets with addresses")
        print("=" * 40)
        
        return results if results else ["No streets found in selected area"]
        
    except Exception as e:
        print(f"Error processing zone: {e}")
        import traceback
        traceback.print_exc()
        return [f"Error: {str(e)}"]

def load_population_data():
    """
    Loads population data from cache if available, otherwise from GPKG.
    Filters for Bucharest and caches the result.
    """
    if os.path.exists(CACHED_POPULATION_FILE):
        print(f"Loading cached population data from {CACHED_POPULATION_FILE}...")
        gdf = gpd.read_file(CACHED_POPULATION_FILE)
        return gdf

    if not os.path.exists(KONTUR_FILE):
        print(f"Error: Kontur file '{KONTUR_FILE}' not found.")
        return None

    print(f"Reading and filtering {KONTUR_FILE} (this may take a moment)...")
    try:
        # Create a bounding box polygon in EPSG:4326
        bbox_poly_4326 = box(*BBOX_COORDS)
        
        # Create a GeoSeries to handle the transformation
        gs_bbox = gpd.GeoSeries([bbox_poly_4326], crs="EPSG:4326")
        
        # Transform to EPSG:3857 (which matches the GPKG file)
        gs_bbox_3857 = gs_bbox.to_crs("EPSG:3857")
        bbox_poly_3857 = gs_bbox_3857.iloc[0]
        
        print(f"Transformed BBox to EPSG:3857: {bbox_poly_3857.bounds}")
        
        # Read file with the transformed bbox filter
        gdf = gpd.read_file(KONTUR_FILE, bbox=bbox_poly_3857)
        
        if gdf.empty:
            print("Warning: No data found within the specified bounding box.")
            return None

        # Ensure CRS is EPSG:4326 for Folium visualization
        if gdf.crs != "EPSG:4326":
            print("Reprojecting data to EPSG:4326 for visualization...")
            gdf = gdf.to_crs("EPSG:4326")

        print(f"Found {len(gdf)} hexagons. Saving filtered data to {CACHED_POPULATION_FILE}...")
        gdf.to_file(CACHED_POPULATION_FILE, driver="GeoJSON")
        
        return gdf
        
    except Exception as e:
        print(f"Error processing population data: {e}")
        return None

def load_neighborhoods():
    """
    Loads neighborhood polygons from GeoJSON.
    """
    if not os.path.exists(NEIGHBORHOODS_FILE):
        print(f"Error: Neighborhoods file '{NEIGHBORHOODS_FILE}' not found.")
        return None
        
    print(f"Loading neighborhoods from {NEIGHBORHOODS_FILE}...")
    try:
        gdf = gpd.read_file(NEIGHBORHOODS_FILE)
        return gdf
    except Exception as e:
        print(f"Error loading neighborhoods: {e}")
        return None

def get_foot_traffic_data():
    """
    Fetches foot traffic forecast from BestTime API.
    """
    params = {
        'api_key_private': API_KEY_PRIVATE,
        'lat': LAT,
        'lng': LNG,
        'radius': RADIUS,
        'types': TYPES,
        'limit': LIMIT,
        'foot_traffic': 'both'
    }

    print(f"\n=== BestTime API Debug Info ===")
    print(f"API Key (first 10 chars): {API_KEY_PRIVATE[:10]}...")
    print(f"Request URL: {BASE_URL}")
    print(f"Parameters: lat={LAT}, lng={LNG}, radius={RADIUS}")
    print(f"Fetching forecast data from BestTime.app...")
    
    try:
        response = requests.get(BASE_URL, params=params)
        
        # Debug: Show response status
        print(f"Response Status Code: {response.status_code}")
        
        # Try to parse JSON response even if status is not OK
        try:
            data = response.json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")
            data = None
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"\n❌ API Error - HTTP {response.status_code}")
            if data:
                print(f"Error Message: {data.get('message', 'No error message provided')}")
                if 'status' in data:
                    print(f"Status: {data.get('status')}")
                if 'quota_exceeded' in str(data).lower() or 'limit' in str(data).lower():
                    print("⚠️  This appears to be a QUOTA or LIMIT error")
                if 'invalid' in str(data).lower() or 'unauthorized' in str(data).lower():
                    print("⚠️  This appears to be an API KEY error")
            print("=" * 40)
            return None
        
        # Check for application-level errors
        if data and data.get('status') == 'error':
            print(f"\n❌ API Application Error: {data.get('message')}")
            print("=" * 40)
            return None
        
        # Success
        venues = data.get('venues', []) if data else []
        print(f"\n✅ API Request Successful! Retrieved {len(venues)} venues")
        print("=" * 40)
        return venues
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network/Request Error: {e}")
        print("=" * 40)
        return None
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("=" * 40)
        return None

def process_traffic_for_heatmap(venues):
    """
    Processes venue data into a list of lists for HeatMapWithTime.
    """
    heatmap_data = [[] for _ in range(24)]
    count = 0
    
    for venue in venues:
        lat = venue.get('venue_lat')
        lng = venue.get('venue_lng')
        day_raw = venue.get('day_raw')
        
        if not lat or not lng or not day_raw or len(day_raw) != 24:
            continue
            
        count += 1
        for hour in range(24):
            intensity = day_raw[hour]
            if intensity is None or intensity == -1:
                intensity = 0
            
            weight = intensity / 100.0
            if weight > 0:
                heatmap_data[hour].append([lat, lng, weight])
                
    print(f"Processed {count} venues for heatmap.")
    return heatmap_data

def create_dual_map(population_gdf, traffic_heatmap_data, neighborhoods_gdf):
    """
    Creates the combined map with all layers.
    """
    print("Generating interactive dual map...")
    
    m = folium.Map(
        location=[LAT, LNG], 
        zoom_start=12, 
        tiles='cartodbdark_matter'
    )

    # --- Layer 1: Residential Density (Static) ---
    if population_gdf is not None:
        print("Adding Residential Density layer...")
        
        # Create a blue-to-red diverging colormap
        min_pop = population_gdf['population'].min()
        max_pop = population_gdf['population'].max()
        
        colormap = cm.LinearColormap(
            colors=['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c'],
            vmin=min_pop,
            vmax=max_pop,
            caption='Population Density'
        )
        
        # Style function using the colormap
        def style_function(feature):
            pop = feature['properties'].get('population', 0)
            color = colormap(pop)
            
            return {
                'fillColor': color,
                'color': color,
                'weight': 1,
                'fillOpacity': 0.4,
                'opacity': 0.4
            }

        # Create FeatureGroup for Population
        fg_population = folium.FeatureGroup(name="Residential Density", overlay=True)
        
        folium.GeoJson(
            population_gdf,
            name="Population Hexagons",
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=['population'],
                aliases=['Residents:'],
                localize=True
            )
        ).add_to(fg_population)
        
        fg_population.add_to(m)

    # --- Layer 2: Neighborhoods (Static) ---
    if neighborhoods_gdf is not None:
        print("Adding Neighborhoods layer...")
        
        def neighborhood_style(feature):
            return {
                'fillColor': feature['properties'].get('color', '#3388ff'),
                'color': feature['properties'].get('color', '#3388ff'),
                'weight': 2,
                'fillOpacity': 0.1,
                'opacity': 0.8
            }
            
        fg_neighborhoods = folium.FeatureGroup(name="Neighborhoods", overlay=True)
        
        folium.GeoJson(
            neighborhoods_gdf,
            name="Neighborhoods",
            style_function=neighborhood_style,
            tooltip=folium.GeoJsonTooltip(
                fields=['name'],
                aliases=['Neighborhood:'],
                localize=True
            )
        ).add_to(fg_neighborhoods)
        
        fg_neighborhoods.add_to(m)

    # --- Layer 3: Commercial Activity (Animated) ---
    if traffic_heatmap_data:
        print("Adding Commercial Activity layer...")
        
        time_index = [f"{h:02d}:00" for h in range(24)]
        
        vivid_gradient = {
            0.2: '#2c7bb6', # Deep Blue
            0.4: '#abd9e9', # Light Blue
            0.6: '#ffffbf', # Pale Yellow
            0.8: '#fdae61', # Orange
            1.0: '#d7191c'  # Deep Red
        }
        
        hm = HeatMapWithTime(
            traffic_heatmap_data,
            index=time_index,
            auto_play=True,
            max_opacity=0.8,
            radius=15,
            gradient=vivid_gradient,
            name="Commercial Activity (Animated)",
            use_local_extrema=False
        )
        hm.add_to(m)

    # --- Custom UI Title Card ---
    title_html = '''
     <div style="position: fixed; 
     top: 20px; right: 20px; width: 300px; height: auto; 
     z-index:9999; font-size:14px;
     background-color: rgba(15, 15, 15, 0.90);
     color: white;
     padding: 20px;
     border-radius: 12px;
     box-shadow: 0 4px 20px rgba(0,0,0,0.6);
     font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
     backdrop-filter: blur(8px);
     border: 1px solid rgba(255,255,255,0.08);">
     <h4 style="margin:0 0 10px 0; font-weight: 700; letter-spacing: 0.5px; color: #00d4ff;">BUCHAREST PULSE</h4>
     
     <div style="margin-bottom: 8px;">
        <span style="color: #feb24c;">●</span> <span style="color:#ccc; font-size:12px;">Residential Density (Static)</span>
     </div>
     <div style="margin-bottom: 8px;">
        <span style="border: 1px solid #fff; display:inline-block; width:10px; height:10px;"></span> <span style="color:#ccc; font-size:12px;">Neighborhoods (Boundaries)</span>
     </div>
     <div style="margin-bottom: 15px;">
        <span style="color: cyan;">●</span> <span style="color:#ccc; font-size:12px;">Commercial Activity (Animated)</span>
     </div>
     
     <p style="margin:0; font-size: 10px; color: #777; text-transform: uppercase;">
        Kontur • BestTime • OSM
     </p>
     </div>
     '''
    m.get_root().html.add_child(folium.Element(title_html))

    # --- Drawing Controls for Zone Selection ---
    draw = Draw(
        export=True,
        filename='drawn_zone.geojson',
        position='topleft',
        draw_options={
            'polyline': False,
            'circle': False,
            'marker': False,
            'circlemarker': False,
            'rectangle': {
                'shapeOptions': {
                    'color': '#00d4ff',
                    'fillColor': '#00d4ff',
                    'fillOpacity': 0.2,
                    'weight': 2
                }
            },
            'polygon': {
                'shapeOptions': {
                    'color': '#00d4ff',
                    'fillColor': '#00d4ff',
                    'fillOpacity': 0.2,
                    'weight': 2
                }
            }
        },
        edit_options={'edit': True}
    )
    draw.add_to(m)

    # --- Street Analysis Panel ---
    street_panel_html = '''
    <style>
        /* Cyberpunk-styled Drawing Toolbar */
        .leaflet-draw-toolbar a {
            background-color: rgba(15, 15, 15, 0.90) !important;
            border: 1px solid rgba(0, 212, 255, 0.3) !important;
            color: #00d4ff !important;
        }
        
        .leaflet-draw-toolbar a:hover {
            background-color: rgba(0, 212, 255, 0.15) !important;
            border-color: #00d4ff !important;
        }
        
        .leaflet-draw-actions a {
            background-color: rgba(15, 15, 15, 0.95) !important;
            color: #00d4ff !important;
            border: 1px solid rgba(0, 212, 255, 0.5) !important;
        }
        
        /* Street Analysis Panel */
        #street-panel {
            position: fixed;
            top: 20px;
            right: 340px;
            width: 320px;
            max-height: 600px;
            z-index: 9998;
            background: rgba(15, 15, 15, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 12px;
            border: 1px solid rgba(0, 212, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: white;
            display: none;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        #street-panel.active {
            display: block;
        }
        
        #street-panel-header {
            padding: 16px 20px;
            background: rgba(0, 212, 255, 0.08);
            border-bottom: 1px solid rgba(0, 212, 255, 0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        #street-panel-header h4 {
            margin: 0;
            font-size: 16px;
            font-weight: 700;
            color: #00d4ff;
            letter-spacing: 0.5px;
        }
        
        #street-panel-buttons {
            display: flex;
            gap: 8px;
        }
        
        .panel-button {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            color: #00d4ff;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }
        
        .panel-button:hover {
            background: rgba(0, 212, 255, 0.2);
            border-color: #00d4ff;
        }
        
        #street-panel-content {
            padding: 20px;
            max-height: 500px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.6;
        }
        
        #street-panel-content::-webkit-scrollbar {
            width: 8px;
        }
        
        #street-panel-content::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        }
        
        #street-panel-content::-webkit-scrollbar-thumb {
            background: rgba(0, 212, 255, 0.3);
            border-radius: 4px;
        }
        
        #street-panel-content::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 212, 255, 0.5);
        }
        
        .street-item {
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(0, 212, 255, 0.05);
            border-left: 3px solid #00d4ff;
            border-radius: 4px;
            color: #ccc;
        }
        
        .street-name {
            font-weight: 600;
            color: #fff;
        }
        
        .street-range {
            color: #00d4ff;
            font-family: 'Courier New', monospace;
        }
        
        .placeholder {
            color: #777;
            text-align: center;
            padding: 40px 20px;
        }
        
        .placeholder-icon {
            font-size: 32px;
            margin-bottom: 12px;
        }
        
        .loading {
            text-align: center;
            color: #00d4ff;
            padding: 40px 20px;
        }
        
        .spinner {
            border: 3px solid rgba(0, 212, 255, 0.1);
            border-top: 3px solid #00d4ff;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    
    <div id="street-panel">
        <div id="street-panel-header">
            <h4>📍 Street Analysis</h4>
            <div id="street-panel-buttons">
                <button class="panel-button" id="copy-btn" title="Copy results">Copy</button>
                <button class="panel-button" id="close-btn" title="Close panel">✕</button>
            </div>
        </div>
        <div id="street-panel-content">
            <div class="placeholder">
                <div class="placeholder-icon">🗺️</div>
                <div>Draw a shape on the map to analyze streets and extract house numbers</div>
            </div>
        </div>
    </div>
    
    <script>
        // Panel management
        function showPanel() {
            document.getElementById('street-panel').classList.add('active');
        }
        
        function hidePanel() {
            document.getElementById('street-panel').classList.remove('active');
        }
        
        function updatePanelContent(html) {
            document.getElementById('street-panel-content').innerHTML = html;
            showPanel();
        }
        
        function showLoading() {
            updatePanelContent(`
                <div class="loading">
                    <div class="spinner"></div>
                    <div>Extracting streets from OpenStreetMap...</div>
                </div>
            `);
        }
        
        function showError(message) {
            updatePanelContent(`
                <div class="placeholder">
                    <div class="placeholder-icon">⚠️</div>
                    <div>${message}</div>
                </div>
            `);
        }
        
        function displayStreets(streets) {
            if (!streets || streets.length === 0) {
                showError('No streets found in selected area');
                return;
            }
            
            let html = '';
            streets.forEach(street => {
                const parts = street.match(/^(.+?)\\s*\\((.+)\\)$/);
                if (parts) {
                    html += `
                        <div class="street-item">
                            <div class="street-name">${parts[1]}</div>
                            <div class="street-range">${parts[2]}</div>
                        </div>
                    `;
                } else {
                    html += `
                        <div class="street-item">
                            <div class="street-name">${street}</div>
                        </div>
                    `;
                }
            });
            
            updatePanelContent(html);
        }
        
        // Mock processing (since we can't call Python from static HTML)
        // In production, this would make an API call to a Flask/FastAPI backend
        function processDrawnZone(geoJsonLayer) {
            showLoading();
            
            const geometry = geoJsonLayer.toGeoJSON().geometry;
            console.log('Drawn geometry:', geometry);
            
            // Simulate processing delay
            setTimeout(() => {
                // Mock data for demonstration
                const mockStreets = [
                    "Calea Victoriei (102-145, 200-250)",
                    "Strada Lipscani (1-25, 50-80)",
                    "Bulevardul Unirii (10-30, 100-150)",
                    "Strada Smârdan (5-15)",
                    "Piața Universității (1-10)"
                ];
                
                displayStreets(mockStreets);
                
                // Log for debugging - in production, send this to backend
                console.log('To process with OSMnx, send this geometry to backend:', 
                    JSON.stringify(geometry.coordinates));
            }, 1500);
        }
        
        // Event handlers for button clicks
        document.getElementById('close-btn').addEventListener('click', hidePanel);
        
        document.getElementById('copy-btn').addEventListener('click', () => {
            const content = document.getElementById('street-panel-content');
            const streetItems = content.querySelectorAll('.street-item');
            
            if (streetItems.length === 0) {
                alert('No streets to copy');
                return;
            }
            
            let text = 'Street Analysis Results:\\n\\n';
            streetItems.forEach(item => {
                const name = item.querySelector('.street-name').textContent;
                const range = item.querySelector('.street-range');
                if (range) {
                    text += `${name} (${range.textContent})\\n`;
                } else {
                    text += `${name}\\n`;
                }
            });
            
            navigator.clipboard.writeText(text).then(() => {
                const btn = document.getElementById('copy-btn');
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied';
                setTimeout(() => {
                    btn.textContent = originalText;
                }, 2000);
            }).catch(err => {
                alert('Failed to copy to clipboard');
            });
        });
        
        // Store current drawn layer for processing
        let currentDrawnLayer = null;
        
        // Function to find the Leaflet map object using multiple methods
        function findLeafletMap() {
            // Method 1: Look for map in global window object (Folium pattern)
            for (let key in window) {
                if (key.startsWith('map_') && window[key] && window[key]._container) {
                    console.log('✅ Found map via global variable:', key);
                    return window[key];
                }
            }
            
            // Method 2: Get from DOM element
            const mapElement = document.querySelector('.folium-map');
            if (mapElement && mapElement._leaflet_id) {
                const map = window[mapElement._leaflet_id];
                if (map) {
                    console.log('✅ Found map via DOM element:', mapElement._leaflet_id);
                    return map;
                }
            }
            
            // Method 3: Search all Leaflet map instances
            if (window.L && window.L.Map) {
                const maps = [];
                for (let key in window) {
                    try {
                        if (window[key] instanceof L.Map) {
                            maps.push(window[key]);
                        }
                    } catch(e) {}
                }
                if (maps.length > 0) {
                    console.log('✅ Found map via L.Map instance search');
                    return maps[0];
                }
            }
            
            console.error('❌ Could not find Leaflet map using any method');
            return null;
        }
        
        // Listen for draw events - setup after DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {
            // Wait for Leaflet map to be available
            setTimeout(() => {
                const leafletMap = findLeafletMap();
                
                if (!leafletMap) {
                    console.error('Could not access Leaflet map object');
                    // Retry after more time
                    setTimeout(() => {
                        const retryMap = findLeafletMap();
                        if (retryMap) {
                            setupDrawListeners(retryMap);
                        } else {
                            console.error('Failed to find map after retry');
                        }
                    }, 2000);
                    return;
                }
                
                setupDrawListeners(leafletMap);
                
            }, 1500);
        });
        
        // Setup all draw event listeners
        function setupDrawListeners(leafletMap) {
            console.log('✅ Setting up draw event listeners...');

                
                // When a shape is drawn
                leafletMap.on('draw:created', function(e) {
                    const layer = e.layer;
                    currentDrawnLayer = layer;
                    
                    // Add the layer to the map
                    leafletMap.addLayer(layer);
                    
                    // Add click handler to show "Extract Addresses" button
                    layer.on('click', function() {
                        showExtractButton(layer, leafletMap);
                    });
                    
                    // Auto-show button hint
                    showPanelMessage('📌 Click the drawn shape to extract addresses');
                });
                
                // When a shape is edited
                leafletMap.on('draw:edited', function(e) {
                    const layers = e.layers;
                    layers.eachLayer(function(layer) {
                        currentDrawnLayer = layer;
                        layer.on('click', function() {
                            showExtractButton(layer, leafletMap);
                        });
                    });
                    showPanelMessage('📌 Click the edited shape to extract addresses');
                });
                
                // When a shape is deleted
                leafletMap.on('draw:deleted', function(e) {
                    currentDrawnLayer = null;
                    updatePanelContent(`
                        <div class="placeholder">
                            <div class="placeholder-icon">🗺️</div>
                            <div>Draw a shape on the map to analyze streets and extract house numbers</div>
                        </div>
                    `);
                });
                
                // Function to show extract button in a popup
                function showExtractButton(layer, map) {
                    const geometry = layer.toGeoJSON().geometry;
                    const center = layer.getBounds().getCenter();
                    
                    // Create popup with Extract button
                    const popupContent = `
                        <div style="text-align: center; padding: 10px;">
                            <button id="extract-btn" style="
                                background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
                                border: none;
                                color: white;
                                padding: 12px 24px;
                                font-size: 14px;
                                font-weight: 600;
                                border-radius: 6px;
                                cursor: pointer;
                                box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
                                transition: all 0.2s;
                                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 16px rgba(0, 212, 255, 0.5)';" 
                               onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 12px rgba(0, 212, 255, 0.3)';">
                                📍 Extract Addresses
                            </button>
                        </div>
                    `;
                    
                    const popup = L.popup({
                        closeButton: true,
                        autoClose: false,
                        closeOnClick: false
                    })
                    .setLatLng(center)
                    .setContent(popupContent)
                    .openOn(map);
                    
                    // Add event listener after popup is added to DOM
                    setTimeout(() => {
                        const extractBtn = document.getElementById('extract-btn');
                        if (extractBtn) {
                            extractBtn.addEventListener('click', function() {
                                processDrawnZone(layer);
                                popup.close();
                            });
                        }
                    }, 100);
                }
                
                // Function to show message in panel without full activation
                function showPanelMessage(message) {
                    updatePanelContent(`
                        <div class="placeholder">
                            <div class="placeholder-icon">💡</div>
                            <div>${message}</div>
                        </div>
                    `);
                }
            } // End of setupDrawListeners function
                
            }, 1500);
        });
    </script>
    '''
    
    m.get_root().html.add_child(folium.Element(street_panel_html))

    # --- Layer Control ---
    folium.LayerControl(position='topleft', collapsed=False).add_to(m)

    # Save
    output_file = 'bucharest_dual_map.html'
    m.save(output_file)
    print(f"\n✓ Map generated successfully: {output_file}")

def main():
    print("--- Starting Bucharest Dual Map Generation ---")
    
    # 1. Load Population
    pop_gdf = load_population_data()
    if pop_gdf is not None:
        print(f"Loaded {len(pop_gdf)} population hexagons.")
    
    # 2. Load Neighborhoods
    neighborhoods_gdf = load_neighborhoods()
    if neighborhoods_gdf is not None:
        print(f"Loaded {len(neighborhoods_gdf)} neighborhoods.")

    # 3. Load Traffic
    venues = get_foot_traffic_data()
    traffic_data = []
    if venues:
        traffic_data = process_traffic_for_heatmap(venues)
    
    # 4. Create Map
    if pop_gdf is None and not traffic_data and neighborhoods_gdf is None:
        print("Error: No data available for any layer.")
        return
        
    create_dual_map(pop_gdf, traffic_data, neighborhoods_gdf)

if __name__ == "__main__":
    main()
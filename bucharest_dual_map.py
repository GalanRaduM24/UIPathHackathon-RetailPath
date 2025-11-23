import folium
from folium.plugins import HeatMapWithTime
import branca.colormap as cm
import geopandas as gpd
import requests
import os
import json
from shapely.geometry import box
import sys
from dotenv import load_dotenv

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
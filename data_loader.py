import os
import json
import requests
import geopandas as gpd
from shapely.geometry import box
from config import (
    CACHED_POPULATION_FILE, KONTUR_FILE, BBOX_COORDS, 
    NEIGHBORHOODS_FILE, STORES_FILE, 
    API_KEY_PRIVATE, BASE_URL, LAT, LNG, RADIUS, TYPES, LIMIT
)

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

def load_competition_data():
    """
    Loads competition store data from JSON file.
    """
    if not os.path.exists(STORES_FILE):
        print(f"Error: Stores file '{STORES_FILE}' not found.")
        return None
        
    print(f"Loading competition data from {STORES_FILE}...")
    try:
        with open(STORES_FILE, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading competition data: {e}")
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
    print(f"API Key (first 10 chars): {str(API_KEY_PRIVATE)[:10]}...")
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
            # print(f"Response JSON: {json.dumps(data, indent=2)}") # Commented out to reduce noise
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

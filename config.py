import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
API_KEY_PRIVATE = os.getenv("BESTTIME_API_KEY")
KONTUR_FILE = "kontur_population_20231101.gpkg"
CACHED_POPULATION_FILE = "bucharest_population_hexagons.geojson"
NEIGHBORHOODS_FILE = "neighborghoods/bucharest_neighborhoods_final.geojson"
STORES_FILE = "stores_with_coords.json"

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

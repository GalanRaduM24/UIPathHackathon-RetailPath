import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get base directory (2 levels up from config.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# --- CONFIGURATION ---
API_KEY_PRIVATE = os.getenv("BESTTIME_API_KEY")
KONTUR_FILE = os.path.join(DATA_DIR, "kontur_population_20231101.gpkg")
CACHED_POPULATION_FILE = os.path.join(DATA_DIR, "bucharest_population_hexagons.geojson")
NEIGHBORHOODS_FILE = os.path.join(DATA_DIR, "neighborghoods", "bucharest_neighborhoods_final.geojson")
STORES_FILE = os.path.join(DATA_DIR, "stores_with_coords.json")

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

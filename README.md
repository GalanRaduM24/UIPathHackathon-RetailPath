# Bucharest Interactive Map

An interactive multi-layer map visualization of Bucharest showing residential population density, neighborhood boundaries, and real-time commercial activity patterns.

![Bucharest Map Preview](bucharest_dual_map.html)

## Features

### 🗺️ Three Interactive Layers

1. **Residential Density** (Static)
   - Population data from [Kontur Population Dataset](https://data.humdata.org/dataset/kontur-population-dataset)
   - 867 hexagonal cells showing population distribution
   - Blue-to-red color gradient indicating density

2. **Neighborhoods** (Static)
   - 60 Bucharest neighborhood boundaries
   - Color-coded polygons with interactive tooltips
   - Hover to see neighborhood names

3. **Commercial Activity** (Animated)
   - Real-time foot traffic data from [BestTime API](https://besttime.app)
   - 500 venues (restaurants, bars, cafes, shopping centers, parks)
   - 24-hour animated heatmap showing activity patterns
   - Auto-playing time-lapse visualization

## Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Denis172003/Uipath.git
   cd Uipath
   ```

2. **Install dependencies**
   ```bash
   pip install folium geopandas requests python-dotenv branca shapely
   ```

3. **Configure API Key**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your BestTime API key:
   ```
   BESTTIME_API_KEY=your_api_key_here
   ```
   
   Get your free API key at: https://besttime.app

4. **Download Population Data** (Optional)
   
   The repository includes cached population data (`bucharest_population_hexagons.geojson`). 
   
   To regenerate from source:
   - Download the Kontur Population dataset: [kontur_population_20231101.gpkg](https://data.humdata.org/dataset/kontur-population-dataset)
   - Place it in the project root directory
   - Delete `bucharest_population_hexagons.geojson` to force regeneration

## Usage

Run the script to generate the interactive map:

```bash
python bucharest_dual_map.py
```

This will:
1. Load population data (from cache or GPKG file)
2. Load neighborhood boundaries
3. Fetch real-time foot traffic data from BestTime API
4. Generate `bucharest_dual_map.html`

Open `bucharest_dual_map.html` in your browser to view the interactive map.

## Project Structure

```
Uipath/
├── bucharest_dual_map.py              # Main script
├── bucharest_dual_map.html            # Generated map output
├── bucharest_population_hexagons.geojson  # Cached population data
├── neighborghoods/
│   ├── bucharest_neighborhoods_final.geojson  # Neighborhood boundaries
│   └── other formats/
│       └── bucharest_neighborhood_names.txt
├── .env                               # API keys (not tracked in git)
├── .env.example                       # Template for environment variables
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

## Configuration

Edit the configuration section in `bucharest_dual_map.py`:

```python
# Bounding box for Bucharest
BBOX_COORDS = [25.90, 44.33, 26.25, 44.55]

# Map center
LAT = 44.4268
LNG = 26.1025

# BestTime API settings
RADIUS = 10000  # Search radius in meters
TYPES = 'BAR,RESTAURANT,CAFE,SHOPPING,PARK'
LIMIT = 500     # Maximum venues to fetch
```

## Data Sources

- **Population Data**: [Kontur Population Dataset](https://data.humdata.org/dataset/kontur-population-dataset) (Global Human Settlement Layer)
- **Foot Traffic**: [BestTime API](https://besttime.app) - Real-time venue activity forecasts
- **Neighborhoods**: Custom GeoJSON with Bucharest administrative boundaries
- **Base Map**: CartoDB Dark Matter tiles

## Technologies

- **[Folium](https://python-visualization.github.io/folium/)** - Interactive map visualization
- **[GeoPandas](https://geopandas.org/)** - Geospatial data processing
- **[Python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment variable management
- **[Branca](https://github.com/python-visualization/branca)** - Color mapping utilities

## API Key Security

⚠️ **Important**: Never commit your `.env` file to version control!

The `.gitignore` file is configured to exclude:
- `.env` (contains your API key)
- Large data files (`*.gpkg`)
- Virtual environments
- OS-specific files

## License

This project is open source and available for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Denis Mitica - [GitHub](https://github.com/Denis172003)

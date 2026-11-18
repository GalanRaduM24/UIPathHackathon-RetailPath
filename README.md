# RetailPath — Bucharest Retail Location Intelligence

> Find the best place to open a store in Bucharest by combining **population density**, **foot traffic**, **competitor locations** and **street-level analysis** on one interactive map.

RetailPath is a hackathon project (UiPath Hackathon) that layers several public and commercial data sources over a map of Bucharest. A React web app hosts the map; a Flask backend serves the map and runs on-demand street analysis for any area you draw.

---

## Table of contents

- [What it does](#what-it-does)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Quick start](#quick-start)
- [Running the app](#running-the-app)
- [Regenerating the map](#regenerating-the-map)
- [API reference](#api-reference)
- [Project structure](#project-structure)
- [Data sources](#data-sources)
- [Configuration & secrets](#configuration--secrets)
- [Troubleshooting](#troubleshooting)
- [Project status](#project-status)
- [Authors](#authors)

---

## What it does

| Map layer | What you see | Source |
|---|---|---|
| **Residential density** | Hexagon grid coloured by population | Kontur Population dataset |
| **Neighborhoods** | Boundaries of ~60 Bucharest neighborhoods | Custom GeoJSON |
| **Commercial activity** | Foot-traffic heatmap over time (bars, restaurants, cafés, shops, parks) | BestTime API |
| **Competition** | Locations of Lidl, Mega Image, Profi, Carrefour and La Doi Pași stores | `data/stores_with_coords.json` |
| **Store traffic** | Hour-by-hour busyness for each competitor store | `data/stores_enriched.json` |
| **Zone analysis** | Draw a polygon → get every street inside it with its house-number ranges | OpenStreetMap via OSMnx |

The web app also includes a landing page and a chatbot sidebar for strategy questions (the chatbot is currently a UI prototype — see [Project status](#project-status)).

---

## How it works

```
                   ┌──────────────────────────────┐
                   │   React app (Vite, port 5173) │
                   │   /       → Landing page      │
                   │   /map    → Map + chatbot     │
                   └──────────────┬───────────────┘
                                  │  /api/*  (proxied in dev)
                                  ▼
                   ┌──────────────────────────────┐
                   │   Flask backend (port 5001)   │
                   │  GET  /api/map-data           │──► pre-generated Folium map (HTML)
                   │  POST /api/analyze            │──► OSMnx → OpenStreetMap streets
                   └──────────────────────────────┘
                                  ▲
                                  │ built offline by generate_map.py
       ┌──────────────┬───────────┴────┬──────────────────┐
   Kontur pop.   Neighborhoods    BestTime API      Store JSON files
```

1. **`generate_map.py`** loads all datasets, calls the BestTime API, and builds one interactive Folium/Leaflet map saved as `frontend_old/templates/bucharest_dual_map.html`.
2. **Flask (`src/app.py`)** serves that map to the React app and handles zone analysis requests.
3. **React (`frontend/`)** embeds the map in an iframe. When you draw a zone, the map posts the polygon to `/analyze`, and the backend returns the streets found inside it.

---

## Tech stack

**Frontend:** React 19 · Vite 7 · React Router 7 · Framer Motion · Lucide icons
**Backend:** Python · Flask · Flask-CORS · python-dotenv
**Geospatial:** GeoPandas · Shapely · OSMnx · Folium / Leaflet · Branca

---

## Quick start

### Prerequisites

- **Python 3.10+** (tested on 3.11)
- **Node.js 18+** and npm
- A **BestTime API key** — only needed if you want to regenerate the map ([get one here](https://besttime.app))

> **Windows tip:** GeoPandas/OSMnx install most reliably with conda (`conda install -c conda-forge geopandas osmnx`). With plain pip, use a recent Python and pip.

### 1. Clone

```bash
git clone https://github.com/Denis172003/Uipath.git
cd Uipath
git checkout real-time-analysis-fixes
```

### 2. Install backend dependencies

```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Set up your environment file

```bash
cp .env.example .env
```

Then open `.env` and add your key:

```
BESTTIME_API_KEY=your_api_key_here
```

> `.env` is git-ignored. **Never commit your real key.**

---

## Running the app

### Development mode (recommended)

Two terminals, with hot reload on the frontend:

```bash
# Terminal 1 — backend
python src/app.py            # → http://localhost:5001

# Terminal 2 — frontend
cd frontend
npm run dev                  # → http://localhost:5173
```

Open **http://localhost:5173**. Vite forwards `/api` and `/analyze` calls to Flask.

### Production mode

Build the frontend once, then let Flask serve everything:

```bash
cd frontend && npm run build && cd ..
python src/app.py
```

Open **http://localhost:5001**.

### Using the map

1. Click **Get Started** on the landing page (or go to `/map`).
2. Turn layers on and off with the layer control in the top-left of the map.
3. Use the **draw tool** to outline an area. The **Street Analysis** panel lists every street inside it with house-number ranges (e.g. `Strada Lipscani: 1-15, 20-34`). Use **Copy** to copy the results.

> Zone analysis downloads live data from OpenStreetMap, so it takes 10–30 seconds per zone. Results are cached locally in `cache/`, so repeat requests are faster.

---

## Regenerating the map

The repo ships with a ready-made map, so **you don't need this to run the app.** Regenerate it when the data or layers change:

```bash
python generate_map.py
```

This writes `frontend_old/templates/bucharest_dual_map.html`. It needs:

- `BESTTIME_API_KEY` in `.env` (for the foot-traffic layer)
- `data/bucharest_population_hexagons.geojson` (included). If this file is missing, the script rebuilds it from the Kontur dataset, which you must download yourself (see [Data sources](#data-sources)).

To test the street-analysis logic without the UI:

```bash
python test_zone_selector.py
```

---

## API reference

### `GET /api/map-data`

Returns the generated interactive map as an HTML page.

| Status | Meaning |
|---|---|
| `200` | Map HTML |
| `404` | Map file not found — run `python generate_map.py` |

### `POST /api/analyze`

Lists the streets and house-number ranges inside a polygon. (`POST /analyze` works too and is used by the embedded map.)

**Request**

```json
{
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[26.0970, 44.4320], [26.0990, 44.4320], [26.0990, 44.4310], [26.0970, 44.4310], [26.0970, 44.4320]]]
  }
}
```

Coordinates use GeoJSON order: `[longitude, latitude]`.

**Example**

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"geometry":{"type":"Polygon","coordinates":[[[26.097,44.432],[26.099,44.432],[26.099,44.431],[26.097,44.431],[26.097,44.432]]]}}'
```

**Errors:** `400` if `geometry` is missing, `500` if the analysis fails (details in the server log).

---

## Project structure

```
.
├── src/
│   └── app.py                    # Flask entry point: API routes + serves React build
├── backend/
│   ├── config/config.py          # Paths, map center, BestTime settings (reads .env)
│   └── services/
│       ├── data_loader.py        # Loads population, neighborhoods, stores; calls BestTime
│       ├── map_layers.py         # Builds each Folium map layer
│       └── utils.py              # Zone analysis: OSMnx streets + house-number ranges
├── frontend/                     # React + Vite app
│   ├── src/pages/                # LandingPage, MapPage
│   ├── src/components/           # landing/, map/, shared/
│   └── vite.config.js            # Dev server + proxy to Flask
├── frontend_old/templates/
│   └── bucharest_dual_map.html   # Generated map (served by /api/map-data)
├── data/                         # GeoJSON + store datasets
├── Images/                       # Store logos used on the map
├── generate_map.py               # Builds the map HTML from all data sources
├── test_zone_selector.py         # Manual test for zone analysis
├── requirements.txt              # Python dependencies
└── .env.example                  # Template for your local .env
```

---

## Data sources

| Dataset | File | Notes |
|---|---|---|
| Population | `data/bucharest_population_hexagons.geojson` | Bucharest extract of the [Kontur Population dataset](https://data.humdata.org/dataset/kontur-population-dataset) (2023-11-01). The full `.gpkg` is too large for git; only needed to rebuild the extract. Place it at `data/kontur_population_20231101.gpkg`. |
| Neighborhoods | `data/neighborghoods/bucharest_neighborhoods_final.geojson` | Neighborhood boundaries |
| Competitor stores | `data/stores_with_coords.json` | Store names, addresses and coordinates |
| Store traffic | `data/stores_enriched.json` | Hourly busyness for each store, by day of week |
| Foot traffic | — (live) | [BestTime API](https://besttime.app), fetched when the map is generated |
| Streets & addresses | `cache/` (auto-created) | [OpenStreetMap](https://www.openstreetmap.org) via OSMnx, © OpenStreetMap contributors, ODbL |
| Basemap | — | CartoDB Dark Matter tiles |

---

## Configuration & secrets

| Variable | Required | Used for |
|---|---|---|
| `BESTTIME_API_KEY` | Only for `generate_map.py` | Fetching the foot-traffic layer |

Other settings live in `backend/config/config.py`: map center, Bucharest bounding box, BestTime search radius, venue types and result limit.

Git ignores these files so secrets and bulky generated data stay local:

- `.env` and any `.env.*` (except `.env.example`), key and credential files
- `*.gpkg` raw datasets
- `cache/` and `data/cache/` (OpenStreetMap responses)
- `venv/`, `node_modules/`, `frontend/dist/`, `__pycache__/`, logs and editor files

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Map page is blank or shows "Map data not found" | Check that `frontend_old/templates/bucharest_dual_map.html` exists, or run `python generate_map.py`. |
| `/api/...` calls fail with a 404 or connection error in dev | Check that Flask is running on port **5001** before starting Vite. |
| `pip install` fails on GeoPandas / Shapely / Fiona | Install the geospatial packages from conda-forge (see [Prerequisites](#prerequisites)). |
| Foot-traffic layer is empty | `BESTTIME_API_KEY` is missing or invalid. The generator prints `API Key configured: NO` when it isn't set. |
| Zone analysis is slow | The first request for an area downloads data from OpenStreetMap. Keep zones small; repeat requests use the cache. |

---

## Project status

Built as a hackathon prototype. Working today:

- ✅ Interactive map with population, neighborhood, foot-traffic, competition and store-traffic layers
- ✅ Draw-a-zone street and house-number analysis
- ✅ React landing page and map page, served by Flask

Not yet built:

- 🚧 The chatbot sidebar returns placeholder replies; it is not connected to an AI backend yet
- 🚧 Income analytics (mentioned on the landing page) has no data layer yet

---

## Authors

- **Denis Mitica** — [@Denis172003](https://github.com/Denis172003)
- RetailPath team — frontend integration

Built for the UiPath Hackathon. Map data © OpenStreetMap contributors.

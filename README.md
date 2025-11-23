# RetailPath - Bucharest Interactive Map Platform

An integrated platform combining a modern React frontend with a powerful Flask backend for analyzing retail locations in Bucharest using interactive maps, population data, and real-time commercial activity patterns.

## Features

### 🎨 Modern React Frontend (RetailPath)
- **Landing Page**: Beautiful hero section with features and how-it-works
- **Interactive Map Page**: Embedded Bucharest map with layer controls
- **Chatbot Sidebar**: Strategy testing and analysis
- **Responsive Design**: Works on desktop and mobile

### 🗺️ Interactive Map Layers
1. **Residential Density** - Population data from Kontur Population Dataset
2. **Neighborhoods** - 60 Bucharest neighborhood boundaries
3. **Commercial Activity** - Real-time foot traffic from BestTime API
4. **Zone Analysis** - Draw zones and analyze street networks with OSMnx

### 🔧 Backend Services
- **Flask API**: RESTful endpoints for map data and zone analysis
- **OSMnx Integration**: Street network analysis for drawn zones
- **CORS Enabled**: Seamless frontend-backend communication

## Project Structure

```
Uipath-real-time-analysis-fixes/
├── frontend/                    # React + Vite application
│   ├── src/
│   │   ├── components/
│   │   │   ├── landing/        # Landing page components
│   │   │   ├── map/            # Map page components
│   │   │   └── shared/         # Shared components
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   └── MapPage.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── frontend_old/               # Backup of original Folium map
│   └── templates/
│       └── bucharest_dual_map.html
├── backend/                    # Flask backend services
│   ├── services/
│   │   └── utils.py           # Zone analysis with OSMnx
│   └── config/
├── src/
│   └── app.py                 # Flask application
├── data/                      # Map data and GeoJSON files
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Denis172003/Uipath.git
   cd Uipath-real-time-analysis-fixes
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-cors geopandas osmnx requests python-dotenv branca shapely folium
   ```

3. **Install Frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure API Key**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your BestTime API key:
   ```
   BESTTIME_API_KEY=your_api_key_here
   ```
   
   Get your free API key at: https://besttime.app

## Development Workflow

### Option 1: Development Mode (Recommended)

Run both servers for hot-reloading during development:

1. **Start Flask Backend** (Terminal 1)
   ```bash
   python src/app.py
   ```
   Backend will run on http://localhost:5001

2. **Start Vite Dev Server** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on http://localhost:5173

3. **Open your browser**
   ```
   http://localhost:5173
   ```

The Vite dev server will proxy API requests to Flask automatically.

### Option 2: Production Mode

Build and serve the production version:

1. **Build React App**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Start Flask Server**
   ```bash
   python src/app.py
   ```

3. **Open your browser**
   ```
   http://localhost:5001
   ```

Flask will serve the built React app from `frontend/dist/`.

## API Endpoints

### GET /api/map-data
Returns the Bucharest interactive map HTML (Folium-generated).

**Response**: HTML file with embedded Leaflet map

### POST /api/analyze
Analyzes a drawn zone and returns street network data.

**Request Body**:
```json
{
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[lng, lat], [lng, lat], ...]]
  }
}
```

**Response**:
```json
{
  "streets": {
    "nodes": [...],
    "edges": [...]
  }
}
```

## Usage

1. **Landing Page**: Navigate to the home page to see RetailPath branding and features
2. **Map Page**: Click "Get Started" or navigate to `/map`
3. **View Map**: The Bucharest interactive map loads automatically
4. **Toggle Layers**: Use layer controls to show/hide different data layers
5. **Analyze Zones**: Draw zones on the map to analyze street networks (coming soon)
6. **Chatbot**: Use the chatbot sidebar for strategy testing

## Technologies

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Framer Motion** - Animations
- **Lucide React** - Icons

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **OSMnx** - Street network analysis
- **GeoPandas** - Geospatial data processing
- **Folium** - Interactive map generation

### Data Sources
- **Population Data**: Kontur Population Dataset
- **Foot Traffic**: BestTime API
- **Neighborhoods**: Custom GeoJSON
- **Base Map**: CartoDB Dark Matter tiles

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for educational and research purposes.

## Authors

- Denis Mitica - [GitHub](https://github.com/Denis172003)
- Frontend Integration - RetailPath Team

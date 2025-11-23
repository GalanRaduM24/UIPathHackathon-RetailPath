# Project Structure

```
Uipath/
├── backend/                    # Backend Python code
│   ├── config/                 # Configuration files
│   │   └── config.py          # App configuration
│   ├── routes/                 # API routes
│   │   └── (app routes will go here)
│   └── services/               # Business logic
│       ├── utils.py           # Street analysis utilities
│       ├── data_loader.py     # Data loading utilities
│       └── map_layers.py      # Map layer utilities
│
├── frontend/                   # Frontend files
│   ├── templates/             # HTML templates
│   │   └── bucharest_dual_map.html
│   └── static/                # Static assets (CSS, JS, images)
│       ├── css/
│       ├── js/
│       └── images/
│
├── data/                       # Data files
│   ├── kontur_population_20231101.gpkg
│   ├── bucharest_population_hexagons.geojson
│   ├── stores_with_coords.json
│   └── metadata files
│
├── cache/                      # Cache files
├── neighborghoods/            # Neighborhood data
├── Images/                    # Project images
│
├── src/                       # Entry point
│   └── app.py                # Flask application
│
├── tests/                     # Test files
│   └── test_zone_selector.py
│
├── venv/                      # Python virtual environment
├── .env                       # Environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## Key Improvements

### Backend Organization
- **config/**: Centralized configuration
- **routes/**: API endpoints separated from business logic
- **services/**: Reusable business logic and utilities

### Frontend Organization
- **templates/**: HTML templates
- **static/**: All static assets (CSS, JS, images)

### Data Organization
- **data/**: All data files in one location
- **cache/**: Temporary cached data

## Next Steps

1. Move templates from root to `frontend/templates/`
2. Move static files to `frontend/static/`
3. Move data files to `data/`
4. Update import paths in `src/app.py`
5. Create `__init__.py` files for proper Python modules

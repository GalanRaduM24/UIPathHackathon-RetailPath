#!/usr/bin/env python3
"""
Generate the Bucharest map HTML with all layers including Store Traffic.
"""
import sys
import os

# Add backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

import folium
from folium.plugins import Draw
from backend.services.data_loader import (
    load_population_data, 
    load_neighborhoods, 
    load_competition_data,
    load_stores_enriched,
    get_foot_traffic_data,
    process_traffic_for_heatmap
)
from backend.services.map_layers import (
    add_population_layer,
    add_neighborhoods_layer,
    add_traffic_layer,
    add_competition_layer,
    add_store_traffic_layer
)
from backend.config.config import LAT, LNG

def generate_map():
    """Generate the map with all layers."""
    print("--- Starting Bucharest Map Generation ---\n")
    
    # Load data
    print("Loading data...")
    pop_gdf = load_population_data()
    neighborhoods_gdf = load_neighborhoods()
    competition_data = load_competition_data()
    stores_enriched = load_stores_enriched()
    
    # Get traffic data
    venues = get_foot_traffic_data()
    traffic_data = []
    if venues:
        traffic_data = process_traffic_for_heatmap(venues)
    
    # Create base map
    print("\nGenerating interactive map...")
    m = folium.Map(
        location=[LAT, LNG], 
        zoom_start=12, 
        tiles='cartodbdark_matter'
    )
    
    # Add all layers
    add_population_layer(m, pop_gdf)
    add_neighborhoods_layer(m, neighborhoods_gdf)
    add_traffic_layer(m, traffic_data)
    add_competition_layer(m, competition_data)
    add_store_traffic_layer(m, stores_enriched)
    
    # Add drawing controls
    draw = Draw(
        export=False,
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
    
    # Add title/legend
    title_html = '''
    <div id="legend" style="position: fixed; 
    top: 20px; right: 20px; width: 280px; 
    z-index:9999; font-size:14px;
    background: linear-gradient(145deg, rgba(20, 20, 30, 0.95), rgba(30, 30, 45, 0.95));
    color: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    font-family: 'Segoe UI', sans-serif;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 212, 255, 0.2);">
    
    <h4 style="margin:0 0 14px 0; font-weight: 600; letter-spacing: 0.5px; color: #00d4ff; font-size: 16px;">
        📍 BUCHAREST PULSE
    </h4>
    
    <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
        <div style="display: flex; align-items: center; padding: 4px;">
            <span style="color: #feb24c;">●</span>
            <span style="color:#e0e0e0; margin-left: 8px;">Residential Density</span>
        </div>
        
        <div style="display: flex; align-items: center; padding: 4px;">
            <span style="border: 2px solid #00d4ff; display:inline-block; width:12px; height:12px; border-radius: 2px;"></span>
            <span style="color:#e0e0e0; margin-left: 8px;">Neighborhoods</span>
        </div>
        
        <div style="display: flex; align-items: center; padding: 4px;">
            <span style="color: cyan;">●</span>
            <span style="color:#e0e0e0; margin-left: 8px;">Commercial Activity</span>
        </div>
        
        <div style="display: flex; align-items: center; padding: 4px;">
            <span style="color: #ff4444;">●</span>
            <span style="color:#e0e0e0; margin-left: 8px;">Competition</span>
        </div>
        
        <div style="display: flex; align-items: center; padding: 4px; background: rgba(0, 212, 255, 0.08); border-radius: 6px;">
            <span style="color: #00d4ff;">●</span>
            <span style="color:#00d4ff; margin-left: 8px; font-weight: 500;">Store Traffic</span>
        </div>
    </div>
    
    <hr style="margin: 12px 0; border: none; border-top: 1px solid rgba(255,255,255,0.1);">
    
    <p style="margin:0; font-size: 10px; color: #999; text-transform: uppercase; letter-spacing: 0.5px;">
        Kontur • BestTime • OSM
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add Street Analysis Panel
    panel_html = '''
    <div id="street-panel" style="display: none;">
        <div id="street-panel-header">
            <h4>📍 Street Analysis</h4>
            <div id="street-panel-buttons">
                <button id="copy-btn" class="panel-button">Copy</button>
                <button id="close-btn" class="panel-button">Close</button>
            </div>
        </div>
        <div id="street-panel-content">
            <div class="placeholder">
                <div class="placeholder-icon">🗺️</div>
                <div>Draw a zone to analyze streets</div>
            </div>
        </div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(panel_html))
    
    # Add Layer Control
    folium.LayerControl(position='topleft', collapsed=False).add_to(m)
    
    # Save to frontend/templates
    output_file = os.path.join(BASE_DIR, 'frontend', 'templates', 'bucharest_dual_map.html')
    m.save(output_file)
    print(f"\n✓ Map generated successfully: {output_file}")
    print("✓ Run 'python src/app.py' to start the server")

if __name__ == "__main__":
    generate_map()

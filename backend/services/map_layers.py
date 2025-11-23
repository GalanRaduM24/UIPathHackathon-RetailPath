import folium
from folium.plugins import HeatMapWithTime, Draw
import branca.colormap as cm
import os

def add_population_layer(m, population_gdf):
    """
    Adds the residential density layer to the map.
    """
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

def add_neighborhoods_layer(m, neighborhoods_gdf):
    """
    Adds the neighborhoods layer to the map.
    """
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

def add_traffic_layer(m, traffic_heatmap_data):
    """
    Adds the commercial activity heatmap layer to the map.
    """
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

def add_store_traffic_layer(m, stores_enriched_data):
    """
    Adds the store traffic layer with color-coded markers based on current traffic.
    """
    if stores_enriched_data:
        print("Adding Store Traffic layer...")
        fg_traffic = folium.FeatureGroup(name="Store Traffic", overlay=True)
        
        # Map store types to icons
        icon_mapping = {
            "lidl_stores": "Images/lidl.png",
            "mega_image_stores": "Images/mega_image.png",
            "profi_stores": "Images/profi.png",
            "la_doi_pasi_stores": "Images/la_doi_pasi.png",
            "carrefour_stores": "Images/carrefour.png"
        }
        
        store_count = 0
        for store_type, stores in stores_enriched_data.items():
            icon_image = icon_mapping.get(store_type)
            
            for store in stores:
                lat = store.get('latitude')
                lng = store.get('longitude')
                name = store.get('name', 'Unknown Store')
                address = store.get('address', 'Unknown Address')
                popular_times = store.get('popular_times', {})
                
                if lat and lng:
                    # Calculate average traffic across all days/hours
                    avg_traffic = 0
                    traffic_data = popular_times.get('traffic_per_hour_per_day', {}) if popular_times else {}
                    if traffic_data:
                        total_traffic = 0
                        count = 0
                        for day, hours in traffic_data.items():
                            for hour_data in hours:
                                total_traffic += hour_data.get('traffic_percentage', 0)
                                count += 1
                        avg_traffic = total_traffic / count if count > 0 else 0
                    
                    # Color code based on average traffic
                    if avg_traffic >= 50:
                        color = '#d7191c'  # Red - High traffic
                        border_color = '#a01510'
                    elif avg_traffic >= 30:
                        color = '#fdae61'  # Orange - Medium traffic
                        border_color = '#e89850'
                    elif avg_traffic >= 15:
                        color = '#ffffbf'  # Yellow - Low-Medium traffic
                        border_color = '#e6e6a0'
                    else:
                        color = '#2c7bb6'  # Blue - Low traffic
                        border_color = '#1e5a7f'
                    
                    # Create popup with traffic info
                    popup_html = f"""
                    <div style="font-family: Arial; min-width: 200px;">
                        <h4 style="margin: 0 0 8px 0; color: #333;">{name}</h4>
                        <p style="margin: 4px 0; font-size: 12px; color: #666;">{address}</p>
                        <hr style="margin: 8px 0; border: none; border-top: 1px solid #ddd;">
                        <p style="margin: 4px 0;"><strong>Avg. Traffic:</strong> {avg_traffic:.1f}%</p>
                    </div>
                    """
                    
                    folium.CircleMarker(
                        location=[lat, lng],
                        radius=8,
                        color=border_color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.8,
                        weight=2,
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{name} - Traffic: {avg_traffic:.1f}%"
                    ).add_to(fg_traffic)
                    
                    store_count += 1
        
        fg_traffic.add_to(m)
        print(f"Added {store_count} store traffic markers.")

def add_competition_layer(m, competition_data):
    """
    Adds the competition markers layer to the map.
    """
    if competition_data:
        print("Adding Competition layer...")
        fg_competition = folium.FeatureGroup(name="Competition", overlay=True)
        
        # Map store types to image files
        # Keys match the JSON structure, Values match the filenames in Images/ folder
        icon_mapping = {
            "lidl_stores": "Images/lidl.png",
            "mega_image_stores": "Images/mega_image.png",
            "profi_stores": "Images/profi.png",
            "la_doi_pasi_stores": "Images/la_doi_pasi.png",
            "carrefour_stores": "Images/carrefour.png"
        }
        
        store_count = 0
        for store_type, stores in competition_data.items():
            icon_image = icon_mapping.get(store_type)
            
            for store in stores:
                lat = store.get('latitude')
                lng = store.get('longitude')
                name = store.get('name', 'Unknown Store')
                address = store.get('address', 'Unknown Address')
                
                if lat and lng:
                    if icon_image and os.path.exists(icon_image):
                        # Use Custom Icon
                        icon = folium.CustomIcon(
                            icon_image,
                            icon_size=(24, 24), # Adjust size as needed
                            popup_anchor=(0, -12)
                        )
                        folium.Marker(
                            location=[lat, lng],
                            icon=icon,
                            popup=folium.Popup(f"<b>{name}</b><br>{address}", max_width=300),
                            tooltip=f"{name}"
                        ).add_to(fg_competition)
                    else:
                        # Fallback to CircleMarker if image missing
                        folium.CircleMarker(
                            location=[lat, lng],
                            radius=6,
                            color='#ff0000',
                            fill=True,
                            fill_color='#ff4444',
                            fill_opacity=0.7,
                            weight=1,
                            popup=folium.Popup(f"<b>{name}</b><br>{address}", max_width=300),
                            tooltip=f"{name}"
                        ).add_to(fg_competition)
                    
                    store_count += 1
        
        fg_competition.add_to(m)
        print(f"Added {store_count} competition markers.")

def add_ui_elements(m):
    """
    Adds UI elements like title card, drawing controls, and street panel.
    """
    # --- Inject External Assets ---
    # 1. CSS
    m.get_root().html.add_child(folium.Element('<link href="assets/style.css" rel="stylesheet">'))
    
    # 2. JS
    m.get_root().html.add_child(folium.Element('<script src="assets/script.js"></script>'))

    # --- Custom UI Title Card ---
    try:
        with open('assets/title_card.html', 'r') as f:
            title_html = f.read()
        m.get_root().html.add_child(folium.Element(title_html))
    except FileNotFoundError:
        print("Warning: assets/title_card.html not found")

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
    try:
        with open('assets/street_panel.html', 'r') as f:
            street_panel_html = f.read()
        m.get_root().html.add_child(folium.Element(street_panel_html))
    except FileNotFoundError:
        print("Warning: assets/street_panel.html not found")
    
    # --- Layer Control ---
    folium.LayerControl(position='topleft', collapsed=False).add_to(m)

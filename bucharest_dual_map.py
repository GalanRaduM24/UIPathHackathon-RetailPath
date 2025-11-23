import folium
import warnings
from config import LAT, LNG
from data_loader import (
    load_population_data, load_neighborhoods, 
    load_competition_data, get_foot_traffic_data, 
    process_traffic_for_heatmap
)
from map_layers import (
    add_population_layer, add_neighborhoods_layer, 
    add_traffic_layer, add_competition_layer, 
    add_ui_elements
)

warnings.filterwarnings('ignore')

def create_dual_map(population_gdf, traffic_heatmap_data, neighborhoods_gdf, competition_data):
    """
    Creates the combined map with all layers.
    """
    print("Generating interactive dual map...")
    
    m = folium.Map(
        location=[LAT, LNG], 
        zoom_start=12, 
        tiles='cartodbdark_matter'
    )

    # Add Layers
    add_population_layer(m, population_gdf)
    add_neighborhoods_layer(m, neighborhoods_gdf)
    add_traffic_layer(m, traffic_heatmap_data)
    add_competition_layer(m, competition_data)
    
    # Add UI Elements
    add_ui_elements(m)

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
    
    # 4. Load Competition
    competition_data = load_competition_data()
    if competition_data:
        total_stores = sum(len(stores) for stores in competition_data.values())
        print(f"Loaded {total_stores} competition stores.")

    # 5. Create Map
    if pop_gdf is None and not traffic_data and neighborhoods_gdf is None and not competition_data:
        print("Error: No data available for any layer.")
        return
        
    create_dual_map(pop_gdf, traffic_data, neighborhoods_gdf, competition_data)

if __name__ == "__main__":
    main()
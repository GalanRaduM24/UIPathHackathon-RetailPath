import osmnx as ox
from shapely.geometry import Polygon

def format_ranges(numbers):
    """
    Format a list of house numbers into ranges with gaps detection.
    Gaps > 20 create separate ranges.
    Example: [1, 2, 3, 50, 51, 52] -> "1-3, 50-52"
    """
    if not numbers:
        return ""
    
    # Convert to integers and sort
    # Convert each entry to a number safely (handles int, float, numeric strings)
    nums = []
    for n in numbers:
        try:
            # Cast to float first then to int to handle values like "12.0"
            num = int(float(n))
            nums.append(num)
        except (ValueError, TypeError):
            # Skip non‑numeric entries
            continue
    nums = sorted(nums)
    
    if not nums:
        return ""
    
    if len(nums) == 1:
        return str(nums[0])
    
    ranges = []
    start = nums[0]
    prev = nums[0]
    
    for i in range(1, len(nums)):
        current = nums[i]
        
        # Gap detection: if gap > 20, close current range and start new one
        if current - prev > 20:
            # Close previous range
            if prev == start:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            # Start new range
            start = current
        
        prev = current
    
    # Close final range
    if prev == start:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")
    
    return ", ".join(ranges)

def process_drawn_zone(polygon_coords):
    """
    Extract streets and house numbers from a drawn polygon using OSMnx.
    
    Args:
        polygon_coords: List of [lng, lat] coordinates defining the polygon
    
    Returns:
        List of formatted street strings with house number ranges
    """
    try:
        print("\n=== Processing Drawn Zone ===")
        
        # Create shapely Polygon from coordinates
        # Convert from [lng, lat] to proper polygon
        poly = Polygon(polygon_coords)
        
        print(f"Polygon bounds: {poly.bounds}")
        
        # Fetch street graph from polygon
        print("Fetching street network from OpenStreetMap...")
        try:
            G = ox.graph_from_polygon(poly, network_type='all')
            print(f"Retrieved {len(G.nodes)} nodes and {len(G.edges)} edges")
        except Exception as e:
            print(f"Warning: Could not fetch street graph: {e}")
            G = None
        
        # Fetch address nodes with house numbers
        print("Fetching address data...")
        try:
            tags = {'addr:housenumber': True}
            addresses = ox.features_from_polygon(poly, tags=tags)
            print(f"Retrieved {len(addresses)} address points")
        except Exception as e:
            print(f"Warning: Could not fetch addresses: {e}")
            addresses = None
        
        if addresses is None or addresses.empty:
            print("No addresses found in this area")
            return ["No addresses found in selected area"]
        
        # Group addresses by street
        street_data = {}
        
        for idx, row in addresses.iterrows():
            # Get street name
            street = row.get('addr:street', 'Unknown Street')
            housenumber = row.get('addr:housenumber', None)
            
            if housenumber and street:
                if street not in street_data:
                    street_data[street] = []
                
                # Extract numeric part of house number
                # Handle formats like "10A", "10-12", etc.
                num_str = ''.join(filter(str.isdigit, str(housenumber)))
                if num_str:
                    street_data[street].append(num_str)
        
        # Format results
        results = []
        for street, numbers in sorted(street_data.items()):
            if numbers:
                range_str = format_ranges(numbers)
                results.append(f"{street} ({range_str})")
            else:
                results.append(street)
        
        print(f"Found {len(results)} streets with addresses")
        print("=" * 40)
        
        return results if results else ["No streets found in selected area"]
        
    except Exception as e:
        print(f"Error processing zone: {e}")
        import traceback
        traceback.print_exc()
        return [f"Error: {str(e)}"]

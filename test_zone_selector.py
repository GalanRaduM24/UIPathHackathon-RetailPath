#!/usr/bin/env python3
"""
Test script to demonstrate OSMnx street extraction functionality.
This shows how the process_drawn_zone function works with a real polygon.
"""

import os
import sys

# Make the backend package importable regardless of where the repo is cloned
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from services.utils import format_ranges, process_drawn_zone

def test_format_ranges():
    """Test the house number range formatting."""
    print("\n=== Testing format_ranges() ===\n")
    
    test_cases = [
        ([1, 2, 3, 4, 5], "1-5"),
        ([1, 2, 3, 50, 51, 52], "1-3, 50-52"),
        ([10], "10"),
        ([1, 2, 5, 6, 30, 31, 32], "1-2, 5-6, 30-32"),
        ([100, 102, 104, 150, 152], "100-104, 150-152"),
    ]
    
    for numbers, expected in test_cases:
        result = format_ranges(numbers)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: {numbers}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}\n")

def test_street_extraction():
    """Test street extraction with a sample polygon in Bucharest city center."""
    print("\n=== Testing process_drawn_zone() ===\n")
    print("Using a small polygon in Bucharest city center (Lipscani area)...\n")
    
    # Small polygon in Old Town Bucharest (Lipscani area)
    # These coordinates cover a small block with known streets
    sample_polygon = [
        [26.0970, 44.4320],  # Northwest corner
        [26.0990, 44.4320],  # Northeast corner
        [26.0990, 44.4310],  # Southeast corner
        [26.0970, 44.4310],  # Southwest corner
        [26.0970, 44.4320],  # Close polygon
    ]
    
    print("Polygon coordinates:")
    for i, coord in enumerate(sample_polygon):
        print(f"  Point {i+1}: [{coord[0]:.4f}, {coord[1]:.4f}]")
    
    print("\nProcessing with OSMnx (this may take 10-30 seconds)...")
    print("=" * 50)
    
    try:
        streets = process_drawn_zone(sample_polygon)
        
        print("\n=== Results ===\n")
        if streets:
            for i, street in enumerate(streets, 1):
                print(f"{i}. {street}")
            print(f"\nTotal: {len(streets)} streets found")
        else:
            print("No streets found in the selected area")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("=" * 60)
    print("Smart Zone Selector - OSMnx Test Suite")
    print("=" * 60)
    
    # Test 1: Format Ranges
    test_format_ranges()
    
    # Test 2: Street Extraction
    print("\n" + "=" * 60)
    print("WARNING: The following test will fetch data from OpenStreetMap")
    print("This requires an internet connection and may take some time.")
    print("=" * 60)
    
    response = input("\nProceed with OSMnx street extraction test? (y/n): ")
    if response.lower() == 'y':
        test_street_extraction()
    else:
        print("\nSkipping OSMnx test.")
    
    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

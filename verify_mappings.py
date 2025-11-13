#!/usr/bin/env python3
"""
Verify that the current UNIT_ID_MAPPINGS in constants.py are correct
by checking if the mapped units have identical stats.
"""

from find_duplicate_artworks import parse_units_js
from utils.constants import UNIT_ID_MAPPINGS
import os

def main():
    units_file = os.path.join('optc-db.github.io', 'common', 'data', 'units.js')
    
    print("Verifying current UNIT_ID_MAPPINGS...")
    print()
    
    # Parse the units data
    units_data = parse_units_js(units_file)
    
    for from_file, to_file in UNIT_ID_MAPPINGS.items():
        from_id = int(from_file.replace('.png', ''))
        to_id = int(to_file.replace('.png', ''))
        
        if from_id in units_data and to_id in units_data:
            from_unit = units_data[from_id]
            to_unit = units_data[to_id]
            
            # Compare stats
            stats_match = (
                from_unit['max_atk'] == to_unit['max_atk'] and
                from_unit['max_hp'] == to_unit['max_hp'] and
                from_unit['max_rcv'] == to_unit['max_rcv'] and
                from_unit['stars'] == to_unit['stars'] and
                from_unit['cost'] == to_unit['cost'] and
                from_unit['type'] == to_unit['type']
            )
            
            status = "✓ MATCH" if stats_match else "✗ DIFFERENT"
            print(f"{from_file} -> {to_file}: {status}")
            print(f"  From: {from_unit['name']}")
            print(f"  To:   {to_unit['name']}")
            
            if not stats_match:
                print(f"  From stats: ATK:{from_unit['max_atk']} HP:{from_unit['max_hp']} RCV:{from_unit['max_rcv']}")
                print(f"  To stats:   ATK:{to_unit['max_atk']} HP:{to_unit['max_hp']} RCV:{to_unit['max_rcv']}")
            
            print()
        else:
            print(f"{from_file} -> {to_file}: ✗ UNIT NOT FOUND")
            if from_id not in units_data:
                print(f"  Unit {from_id} not found in data")
            if to_id not in units_data:
                print(f"  Unit {to_id} not found in data")
            print()

if __name__ == '__main__':
    main()
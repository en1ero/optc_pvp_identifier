#!/usr/bin/env python3
"""
Script to find characters with multiple artworks by analyzing unit stats.
This identifies units that are the same character with different IDs but identical stats.
"""

import os
import re
import json
from collections import defaultdict
from utils.file_utils import make_file_list

def parse_units_js(file_path):
    """Parse the units.js file to extract unit data"""
    units = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the array content between [ and ];
    start = content.find('window.units = [')
    if start == -1:
        print("Could not find units array in file")
        return {}
    
    start += len('window.units = [')
    end = content.rfind('];')
    if end == -1:
        print("Could not find end of units array")
        return {}
    
    array_content = content[start:end]
    
    # Split by lines and parse each unit entry
    lines = array_content.split('\n')
    unit_id = 0  # Start from 0, will increment to 1 for first unit
    
    for line in lines:
        line = line.strip()
        if line.startswith('[') and line.endswith('],') or line.endswith(']'):
            try:
                # Clean up the line
                if line.endswith(','):
                    line = line[:-1]
                
                # Parse the array - it's a JavaScript array, so we need to handle it carefully
                # Convert to valid JSON format
                json_line = line.replace("'", '"')
                
                # Handle arrays within arrays (like class arrays)
                unit_data = eval(line)  # Using eval since it's JavaScript-like syntax
                
                if len(unit_data) >= 16:  # Ensure we have enough data
                    name = unit_data[0]
                    type_color = unit_data[1]
                    classes = unit_data[2]
                    stars = unit_data[3]
                    cost = unit_data[4]
                    combo = unit_data[5]
                    sockets = unit_data[6]
                    max_level = unit_data[7]
                    max_exp = unit_data[8]
                    min_atk = unit_data[9]
                    min_hp = unit_data[10]
                    min_rcv = unit_data[11]
                    max_atk = unit_data[12]
                    max_hp = unit_data[13]
                    max_rcv = unit_data[14]
                    growth_rate = unit_data[15]
                    
                    # Create a stats signature for comparison (convert classes to string for hashing)
                    classes_str = str(sorted(classes)) if isinstance(classes, list) else str(classes)
                    stats_signature = (max_atk, max_hp, max_rcv, stars, cost, type_color, classes_str)
                    
                unit_id += 1  # Increment first, so first unit gets ID 1
                
                if len(unit_data) >= 16:  # Ensure we have enough data
                    name = unit_data[0]
                    type_color = unit_data[1]
                    classes = unit_data[2]
                    stars = unit_data[3]
                    cost = unit_data[4]
                    combo = unit_data[5]
                    sockets = unit_data[6]
                    max_level = unit_data[7]
                    max_exp = unit_data[8]
                    min_atk = unit_data[9]
                    min_hp = unit_data[10]
                    min_rcv = unit_data[11]
                    max_atk = unit_data[12]
                    max_hp = unit_data[13]
                    max_rcv = unit_data[14]
                    growth_rate = unit_data[15]
                    
                    # Create a stats signature for comparison (convert classes to string for hashing)
                    classes_str = str(sorted(classes)) if isinstance(classes, list) else str(classes)
                    stats_signature = (max_atk, max_hp, max_rcv, stars, cost, type_color, classes_str)
                    
                    units[unit_id] = {
                        'name': name,
                        'type': type_color,
                        'classes': classes,
                        'stars': stars,
                        'cost': cost,
                        'max_atk': max_atk,
                        'max_hp': max_hp,
                        'max_rcv': max_rcv,
                        'stats_signature': stats_signature
                    }
                
            except Exception as e:
                # Skip malformed lines
                continue
    
    return units

def find_duplicate_stats(units_data):
    """Find units with identical stats (same character, different IDs)"""
    
    # Group units by their stats signature
    stats_groups = defaultdict(list)
    
    for unit_id, unit_info in units_data.items():
        try:
            stats_signature = unit_info['stats_signature']
            stats_groups[stats_signature].append((unit_id, unit_info))
        except TypeError as e:
            print(f"Error with unit {unit_id}: {e}")
            print(f"Stats signature: {unit_info['stats_signature']}")
            # Skip this unit
            continue
    
    # Find groups with multiple units (same stats, different IDs)
    duplicates = {}
    for stats_sig, units_list in stats_groups.items():
        if len(units_list) > 1:
            # Sort by unit ID
            units_list.sort(key=lambda x: x[0])
            duplicates[stats_sig] = units_list
    
    return duplicates

def check_artwork_exists(unit_id, thumbnail_path):
    """Check if artwork exists for a given unit ID"""
    png_files = make_file_list(thumbnail_path, '.png')
    target_filename = f"{unit_id:04d}.png"
    
    for file_path in png_files:
        if os.path.basename(file_path) == target_filename:
            return True
    return False

def generate_mapping_suggestions(duplicate_stats, thumbnail_path):
    """Generate mapping suggestions for units with identical stats"""
    
    suggestions = []
    
    for stats_sig, units_list in duplicate_stats.items():
        if len(units_list) == 2:  # Focus on pairs for now
            unit1_id, unit1_info = units_list[0]
            unit2_id, unit2_info = units_list[1]
            
            # Check if both units have artwork
            artwork1_exists = check_artwork_exists(unit1_id, thumbnail_path)
            artwork2_exists = check_artwork_exists(unit2_id, thumbnail_path)
            
            if artwork1_exists and artwork2_exists:
                # Suggest mapping the higher ID to the lower ID (keep the original)
                from_file = f"{unit2_id:04d}.png"
                to_file = f"{unit1_id:04d}.png"
                
                suggestions.append({
                    'from_file': from_file,
                    'to_file': to_file,
                    'unit1_id': unit1_id,
                    'unit2_id': unit2_id,
                    'name': unit1_info['name'],
                    'stats': f"ATK:{unit1_info['max_atk']} HP:{unit1_info['max_hp']} RCV:{unit1_info['max_rcv']}"
                })
    
    return suggestions

def main():
    thumbnail_path = os.path.join('optc-db.github.io', 'api', 'images', 'thumbnail')
    units_file = os.path.join('optc-db.github.io', 'common', 'data', 'units.js')
    
    print("Analyzing unit data for characters with identical stats but different IDs...")
    print(f"Units file: {units_file}")
    print(f"Thumbnail path: {thumbnail_path}")
    print()
    
    # Parse the units data
    print("Parsing units.js file...")
    units_data = parse_units_js(units_file)
    print(f"Loaded {len(units_data)} units")
    
    # Find units with duplicate stats
    print("\nFinding units with identical stats...")
    duplicate_stats = find_duplicate_stats(units_data)
    
    if not duplicate_stats:
        print("No units with identical stats found.")
        return
    
    print(f"Found {len(duplicate_stats)} groups of units with identical stats:")
    print()
    
    # Show the duplicates
    print("=== UNITS WITH IDENTICAL STATS ===")
    for i, (stats_sig, units_list) in enumerate(duplicate_stats.items()):
        if i >= 20:  # Limit output
            print(f"... and {len(duplicate_stats) - 20} more groups")
            break
            
        print(f"\nGroup {i+1}: {len(units_list)} units with identical stats")
        for unit_id, unit_info in units_list:
            artwork_exists = check_artwork_exists(unit_id, thumbnail_path)
            artwork_status = "✓" if artwork_exists else "✗"
            print(f"  ID {unit_id:4d} {artwork_status} - {unit_info['name']}")
        
        # Show stats for the group
        first_unit = units_list[0][1]
        print(f"    Stats: ATK:{first_unit['max_atk']} HP:{first_unit['max_hp']} RCV:{first_unit['max_rcv']} "
              f"Stars:{first_unit['stars']} Cost:{first_unit['cost']} Type:{first_unit['type']}")
    
    # Generate mapping suggestions
    print("\n=== SUGGESTED MAPPINGS ===")
    print("# Add these to UNIT_ID_MAPPINGS in utils/constants.py:")
    print("# (Maps higher ID to lower ID for same character)")
    print()
    
    suggestions = generate_mapping_suggestions(duplicate_stats, thumbnail_path)
    
    if suggestions:
        print("UNIT_ID_MAPPINGS = {")
        for suggestion in suggestions[:20]:  # Limit to first 20
            print(f'    "{suggestion["from_file"]}": "{suggestion["to_file"]}",  '
                  f'# {suggestion["name"]} - IDs {suggestion["unit1_id"]}/{suggestion["unit2_id"]}')
        
        if len(suggestions) > 20:
            print(f"    # ... and {len(suggestions) - 20} more suggestions")
        
        print("}")
        
        print(f"\nTotal suggestions: {len(suggestions)}")
    else:
        print("No mapping suggestions generated (no units found with both artworks)")
    
    print()
    print("Note: Review these suggestions manually to ensure they represent")
    print("the same character with different artworks before adding to constants.py!")

if __name__ == '__main__':
    main()
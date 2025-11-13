#!/usr/bin/env python3
"""
Simple script to check specific unit IDs by counting array entries properly
"""

import os
import re

def get_unit_by_id(units_file, unit_id):
    """Get unit data by ID by properly counting array entries"""
    
    with open(units_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the start of the array
    start = content.find('window.units = [')
    if start == -1:
        return None
    
    start += len('window.units = [')
    end = content.rfind('];')
    if end == -1:
        return None
    
    array_content = content[start:end]
    
    # Split by array entries (look for lines that start with [ and end with ],)
    lines = array_content.split('\n')
    current_unit_id = 0
    
    for line in lines:
        line = line.strip()
        if line.startswith('[') and (line.endswith('],') or line.endswith(']')):
            current_unit_id += 1
            
            if current_unit_id == unit_id:
                # Parse this line
                try:
                    if line.endswith(','):
                        line = line[:-1]
                    
                    # Use eval to parse the JavaScript array
                    unit_data = eval(line)
                    
                    if len(unit_data) >= 16:
                        return {
                            'id': unit_id,
                            'name': unit_data[0],
                            'type': unit_data[1],
                            'classes': unit_data[2],
                            'stars': unit_data[3],
                            'cost': unit_data[4],
                            'max_atk': unit_data[12],
                            'max_hp': unit_data[13],
                            'max_rcv': unit_data[14]
                        }
                except:
                    continue
    
    return None

def main():
    units_file = os.path.join('optc-db.github.io', 'common', 'data', 'units.js')
    
    # Check the specific units mentioned
    unit_ids = [3877, 3878, 4152, 4153]
    
    print("Checking specific units:")
    for unit_id in unit_ids:
        unit = get_unit_by_id(units_file, unit_id)
        if unit:
            print(f"ID {unit_id}: {unit['name']}")
            print(f"  Stats: ATK:{unit['max_atk']} HP:{unit['max_hp']} RCV:{unit['max_rcv']} Stars:{unit['stars']} Cost:{unit['cost']}")
            print(f"  Type: {unit['type']}, Classes: {unit['classes']}")
            print()
        else:
            print(f"ID {unit_id}: NOT FOUND")
            print()

if __name__ == '__main__':
    main()
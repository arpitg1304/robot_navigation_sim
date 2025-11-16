#!/bin/bash
# Preview all maps in the maps directory

echo "Available maps in maps/ directory:"
echo "=================================="

# Find all target files
for file in maps/*_target.npy; do
    if [ -f "$file" ]; then
        # Extract map name (remove path and _target.npy suffix)
        map_name=$(basename "$file" _target.npy)

        # Check if corresponding obstacles file exists
        if [ -f "maps/${map_name}_obstacles.npy" ]; then
            echo "  - $map_name"
        fi
    fi
done

echo ""
echo "To preview a map, run:"
echo "  python tools/preview_map.py <map_name>"
echo ""
echo "Or run this script with a map name:"
echo "  ./preview_all_maps.sh <map_name>"

# If argument provided, preview that map
if [ ! -z "$1" ]; then
    echo ""
    echo "Previewing: $1"
    python tools/preview_map.py "$1"
fi

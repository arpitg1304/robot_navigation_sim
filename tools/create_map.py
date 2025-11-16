#!/usr/bin/env python3
"""
Template script for creating maps programmatically.

Edit this file to create your custom map, then run:
    python tools/create_map.py

Your map will be saved to maps/ directory.
"""

import numpy as np
from pathlib import Path


def create_custom_map():
    """Create a custom map. Modify this function to create your map!"""

    # ========================================
    # EDIT THIS SECTION
    # ========================================

    # Map name (files will be saved as: {name}_target.npy and {name}_obstacles.npy)
    map_name = "my_custom_map"

    # Define target position [x, y]
    # Canvas size is 700x700, coordinates from (0,0) top-left to (700,700) bottom-right
    target = [[600, 600]]  # Target in bottom-right

    # Define obstacles
    # Circles: [x, y] - will have radius 45 (configurable in config.py)
    # Polygons: [x1, y1, x2, y2, x3, y3, ...] - list all vertices
    obstacles = [
        # Example circles
        [150, 150],  # Circle obstacle 1
        [300, 200],  # Circle obstacle 2
        [450, 350],  # Circle obstacle 3

        # Example polygon (rectangle)
        # [x1, y1, x2, y2, x3, y3, x4, y4]
        [100, 400, 200, 400, 200, 500, 100, 500],

        # Example polygon (triangle)
        [550, 100, 600, 150, 550, 200],
    ]

    # ========================================
    # END EDIT SECTION
    # ========================================

    return map_name, target, obstacles


def save_map(map_name, target, obstacles):
    """Save map to files."""
    # Create maps directory
    maps_dir = Path("maps")
    maps_dir.mkdir(exist_ok=True)

    # Convert to numpy arrays
    target_data = np.array(target)
    obstacles_data = np.array(obstacles, dtype=object)

    # Save files
    target_file = maps_dir / f"{map_name}_target.npy"
    obstacles_file = maps_dir / f"{map_name}_obstacles.npy"

    np.save(target_file, target_data)
    np.save(obstacles_file, obstacles_data, allow_pickle=True)

    # Print summary
    print("=" * 60)
    print("Map Created Successfully!")
    print("=" * 60)
    print(f"Map name: {map_name}")
    print(f"Target: {target[0]}")
    print(f"Obstacles: {len(obstacles)}")
    print(f"\nFiles saved:")
    print(f"  {target_file}")
    print(f"  {obstacles_file}")
    print("\nTo use this map in the simulator:")
    print("1. Edit src/main.py")
    print("2. In _load_default_map(), change the file paths to:")
    print(f"   target_file = maps_path / '{map_name}_target.npy'")
    print(f"   obstacles_file = maps_path / '{map_name}_obstacles.npy'")
    print("3. Run: python -m src.main")
    print("=" * 60)


def validate_map(target, obstacles):
    """Validate the map data."""
    errors = []

    # Check target
    if not target or len(target) == 0:
        errors.append("No target defined")
    elif len(target[0]) != 2:
        errors.append("Target must be [x, y]")
    else:
        x, y = target[0]
        if not (0 <= x <= 700):
            errors.append(f"Target x={x} out of bounds (0-700)")
        if not (0 <= y <= 700):
            errors.append(f"Target y={y} out of bounds (0-700)")

    # Check obstacles
    for i, obs in enumerate(obstacles):
        if len(obs) == 2:  # Circle
            x, y = obs
            if not (0 <= x <= 700):
                errors.append(f"Obstacle {i} (circle) x={x} out of bounds")
            if not (0 <= y <= 700):
                errors.append(f"Obstacle {i} (circle) y={y} out of bounds")
        elif len(obs) >= 4:  # Polygon
            if len(obs) % 2 != 0:
                errors.append(f"Obstacle {i} (polygon) has odd number of coordinates")
            for j in range(0, len(obs), 2):
                x, y = obs[j], obs[j+1]
                if not (0 <= x <= 700):
                    errors.append(f"Obstacle {i} (polygon) point {j//2} x={x} out of bounds")
                if not (0 <= y <= 700):
                    errors.append(f"Obstacle {i} (polygon) point {j//2} y={y} out of bounds")
        else:
            errors.append(f"Obstacle {i} has invalid format (need 2 coords for circle, 4+ for polygon)")

    return errors


def main():
    """Main function."""
    print("Creating map...")

    # Create the map
    map_name, target, obstacles = create_custom_map()

    # Validate
    errors = validate_map(target, obstacles)
    if errors:
        print("\n⚠ Validation Errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the errors and try again.")
        return

    print("✓ Validation passed")

    # Save
    save_map(map_name, target, obstacles)


if __name__ == "__main__":
    main()

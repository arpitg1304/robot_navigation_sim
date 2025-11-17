#!/usr/bin/env python3
"""Add default start.npy files to existing maps that don't have one."""

from pathlib import Path
import numpy as np


def add_start_positions():
    """Add start.npy to all maps that don't have it."""
    maps_dir = Path("maps")

    if not maps_dir.exists():
        print("No maps directory found!")
        return

    updated = []
    for map_folder in maps_dir.iterdir():
        if not map_folder.is_dir():
            continue

        # Check if this is a valid map folder
        target_file = map_folder / "target.npy"
        obstacles_file = map_folder / "obstacles.npy"
        start_file = map_folder / "start.npy"

        if not (target_file.exists() and obstacles_file.exists()):
            continue  # Not a valid map

        # Add start.npy if it doesn't exist
        if not start_file.exists():
            default_start = np.array([[350, 200]])
            np.save(start_file, default_start)
            print(f"✓ Added start position to '{map_folder.name}' (default: 350, 200)")
            updated.append(map_folder.name)
        else:
            print(f"  '{map_folder.name}' already has start position")

    print()
    if updated:
        print("=" * 60)
        print(f"Added start positions to {len(updated)} maps:")
        for name in updated:
            print(f"  • {name}")
        print("=" * 60)
    else:
        print("All maps already have start positions!")


if __name__ == "__main__":
    add_start_positions()

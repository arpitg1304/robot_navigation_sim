#!/usr/bin/env python3
"""Migrate old map format to new folder-based structure.

Old format: maps/mapname_target.npy and maps/mapname_obstacles.npy
New format: maps/mapname/target.npy and maps/mapname/obstacles.npy
"""

from pathlib import Path
import shutil

def migrate_maps():
    """Migrate all maps from old format to new folder structure."""
    maps_dir = Path("maps")

    if not maps_dir.exists():
        print("No maps directory found!")
        return

    # Find all old-format target files
    migrated = []
    for target_file in maps_dir.glob("*_target.npy"):
        map_name = target_file.stem.replace("_target", "")
        obstacles_file = maps_dir / f"{map_name}_obstacles.npy"

        if not obstacles_file.exists():
            print(f"⚠ Skipping {map_name} - missing obstacles file")
            continue

        # Create new folder
        map_folder = maps_dir / map_name
        map_folder.mkdir(exist_ok=True)

        # Copy files to new location
        new_target = map_folder / "target.npy"
        new_obstacles = map_folder / "obstacles.npy"

        shutil.copy2(target_file, new_target)
        shutil.copy2(obstacles_file, new_obstacles)

        print(f"✓ Migrated '{map_name}' to {map_folder}/")
        migrated.append(map_name)

    if migrated:
        print()
        print("=" * 60)
        print(f"Successfully migrated {len(migrated)} maps:")
        for name in migrated:
            print(f"  • {name}")
        print()
        print("Old files are still in maps/ directory.")
        print("You can delete them manually if migration was successful:")
        print("  rm maps/*_target.npy maps/*_obstacles.npy")
        print("=" * 60)
    else:
        print("No old-format maps found to migrate.")

if __name__ == "__main__":
    migrate_maps()

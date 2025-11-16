#!/usr/bin/env python3
"""List all available maps in the maps directory."""

from pathlib import Path
import sys


def list_maps():
    """List all maps in the maps directory."""
    maps_dir = Path("maps")

    if not maps_dir.exists():
        print("Maps directory not found!")
        print("Create it with: mkdir maps")
        return []

    # Find all map folders
    maps = {}
    for map_folder in maps_dir.iterdir():
        if map_folder.is_dir():
            target_file = map_folder / "target.npy"
            obstacles_file = map_folder / "obstacles.npy"

            if target_file.exists() and obstacles_file.exists():
                maps[map_folder.name] = {
                    'target': target_file,
                    'obstacles': obstacles_file,
                    'folder': map_folder
                }

    return maps


def print_maps(maps):
    """Print available maps."""
    print("=" * 60)
    print("Available Maps")
    print("=" * 60)

    if not maps:
        print("No maps found in maps/ directory")
        print("\nCreate a map using:")
        print("  1. python -m tools.map_editor")
        print("  2. python tools/create_map.py")
        return

    for map_name in sorted(maps.keys()):
        print(f"  • {map_name}")

    print()
    print(f"Total maps: {len(maps)}")
    print()
    print("Commands:")
    print(f"  Preview: python tools/preview_map.py <map_name>")
    print(f"  Edit:    python -m tools.map_editor")
    print(f"  Create:  python tools/create_map.py")


def main():
    """Main function."""
    maps = list_maps()
    print_maps(maps)

    # If map name provided, preview it
    if len(sys.argv) > 1:
        map_name = sys.argv[1]
        if map_name in maps:
            print()
            print(f"Launching preview for: {map_name}")
            import subprocess
            subprocess.run([sys.executable, "tools/preview_map.py", map_name])
        else:
            print()
            print(f"Error: Map '{map_name}' not found")


if __name__ == "__main__":
    main()

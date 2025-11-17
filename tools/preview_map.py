#!/usr/bin/env python3
"""
Preview a map file without running the full simulator.

Usage:
    python tools/preview_map.py my_map
    python tools/preview_map.py custom_map

This will preview maps/my_map_target.npy and maps/my_map_obstacles.npy
"""

import pygame
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import COLOR_CANVAS_BG, COLOR_OBSTACLE, COLOR_TARGET, COLOR_BLACK, COLOR_WHITE


def preview_map(map_name: str):
    """Preview a map."""
    # Load map files from folder structure
    maps_dir = Path("maps")
    map_folder = maps_dir / map_name
    target_file = map_folder / "target.npy"
    start_file = map_folder / "start.npy"
    obstacles_file = map_folder / "obstacles.npy"

    if not target_file.exists() or not obstacles_file.exists():
        print(f"Error: Map '{map_name}' not found")
        print(f"Looking for: {map_folder}/")
        return

    # Load data
    target_data = np.load(target_file, allow_pickle=True)
    obstacles_data = np.load(obstacles_file, allow_pickle=True)

    target = target_data[0]
    obstacles = list(obstacles_data)

    # Load robot start position
    if start_file.exists():
        start_data = np.load(start_file, allow_pickle=True)
        robot_start = start_data[0]
    else:
        robot_start = [350, 200]  # Default

    # Print info
    print("=" * 60)
    print(f"Map Preview: {map_name}")
    print("=" * 60)
    print(f"Robot Start: ({robot_start[0]:.1f}, {robot_start[1]:.1f})")
    print(f"Target: ({target[0]:.1f}, {target[1]:.1f})")
    print(f"Obstacles: {len(obstacles)}")
    print()
    print("Obstacle details:")
    for i, obs in enumerate(obstacles):
        if len(obs) == 2:
            print(f"  {i}: Circle at ({obs[0]:.1f}, {obs[1]:.1f})")
        else:
            print(f"  {i}: Polygon with {len(obs)//2} vertices")
    print()
    print("Press ESC to close preview")
    print("=" * 60)

    # Initialize pygame
    pygame.init()
    width, height = 700, 700
    screen = pygame.display.set_mode((width, height + 50))
    pygame.display.set_caption(f"Map Preview: {map_name}")

    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Draw
        screen.fill(COLOR_WHITE)

        # Canvas background
        canvas_rect = pygame.Rect(0, 0, width, height)
        pygame.draw.rect(screen, COLOR_CANVAS_BG, canvas_rect)

        # Grid
        grid_color = (220, 220, 225)
        for x in range(0, width, 50):
            pygame.draw.line(screen, grid_color, (x, 0), (x, height), 1)
        for y in range(0, height, 50):
            pygame.draw.line(screen, grid_color, (0, y), (width, y), 1)

        # Obstacles
        for obs in obstacles:
            if len(obs) == 2:  # Circle
                pygame.draw.circle(screen, COLOR_OBSTACLE, (int(obs[0]), int(obs[1])), 45)
                pygame.draw.circle(screen, COLOR_BLACK, (int(obs[0]), int(obs[1])), 45, 2)
            else:  # Polygon
                points = [(obs[i], obs[i+1]) for i in range(0, len(obs), 2)]
                pygame.draw.polygon(screen, COLOR_OBSTACLE, points)
                pygame.draw.polygon(screen, COLOR_BLACK, points, 2)

        # Target
        pygame.draw.circle(screen, COLOR_TARGET, (int(target[0]), int(target[1])), 25)
        pygame.draw.circle(screen, (255, 255, 0), (int(target[0]), int(target[1])), 15)
        pygame.draw.circle(screen, COLOR_WHITE, (int(target[0]), int(target[1])), 4)

        # Robot start position
        start_x, start_y = int(robot_start[0]), int(robot_start[1])
        pygame.draw.circle(screen, (59, 130, 246), (start_x, start_y), 12)
        pygame.draw.circle(screen, COLOR_BLACK, (start_x, start_y), 12, 2)
        pygame.draw.circle(screen, COLOR_WHITE, (start_x, start_y), 3)

        # Info bar
        info_rect = pygame.Rect(0, height, width, 50)
        pygame.draw.rect(screen, (40, 40, 45), info_rect)

        info_text = font.render(
            f"{map_name}: {len(obstacles)} obstacles | Start: ({robot_start[0]:.0f}, {robot_start[1]:.0f}) | Target: ({target[0]:.0f}, {target[1]:.0f})",
            True,
            COLOR_WHITE,
        )
        screen.blit(info_text, (20, height + 15))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Preview closed")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python tools/preview_map.py <map_name>")
        print()
        print("Available maps:")
        maps_dir = Path("maps")
        if maps_dir.exists():
            maps = []
            for map_folder in maps_dir.iterdir():
                if map_folder.is_dir():
                    target_file = map_folder / "target.npy"
                    obstacles_file = map_folder / "obstacles.npy"
                    if target_file.exists() and obstacles_file.exists():
                        maps.append(map_folder.name)

            if maps:
                for map_name in sorted(maps):
                    print(f"  - {map_name}")
            else:
                print("  (No maps found in maps/ directory)")
        else:
            print("  (maps/ directory not found)")
        return

    map_name = sys.argv[1]
    preview_map(map_name)


if __name__ == "__main__":
    main()

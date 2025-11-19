"""Create a challenging map with diverse obstacles for RL training and testing.

This map includes:
- Narrow corridors
- Dense obstacle clusters
- Open spaces
- Strategic placement requiring smart navigation
"""

import numpy as np
from pathlib import Path


def create_challenge_map():
    """Create an advanced challenge map."""

    # Start position (bottom-left area)
    start_position = [(150, 550)]

    # Target position (top-right area)
    target_position = [(550, 150)]

    # Obstacles - mix of circles and polygons
    obstacles = []

    # === 1. Entrance corridor (forces specific path) ===
    # Left wall
    obstacles.append([80, 400, 80, 600, 120, 600, 120, 400])
    # Right wall with gap
    obstacles.append([200, 400, 200, 500, 240, 500, 240, 400])
    obstacles.append([200, 520, 200, 600, 240, 600, 240, 520])

    # === 2. Central maze section ===
    # Horizontal barriers
    obstacles.append([150, 350, 450, 350, 450, 380, 150, 380])
    obstacles.append([250, 250, 550, 250, 550, 280, 250, 280])

    # Vertical barriers
    obstacles.append([320, 280, 320, 450, 350, 450, 350, 280])
    obstacles.append([420, 150, 420, 350, 450, 350, 450, 150])

    # === 3. Circular obstacle cluster (middle-left) ===
    obstacles.append([180, 280])  # Circle
    obstacles.append([220, 250])  # Circle
    obstacles.append([180, 220])  # Circle
    obstacles.append([220, 190])  # Circle

    # === 4. Diamond/polygon obstacles (create interesting paths) ===
    # Diamond 1
    obstacles.append([500, 400, 520, 420, 500, 440, 480, 420])
    # Diamond 2
    obstacles.append([560, 350, 580, 370, 560, 390, 540, 370])

    # === 5. Narrow passage obstacles ===
    # Create a narrow S-curve path
    obstacles.append([350, 450, 380, 450, 380, 550, 350, 550])
    obstacles.append([280, 500, 310, 500, 310, 600, 280, 600])

    # === 6. Guard obstacles near target ===
    # Circle cluster near goal (requires precision)
    obstacles.append([480, 180])  # Circle
    obstacles.append([520, 200])  # Circle
    obstacles.append([490, 120])  # Circle
    obstacles.append([580, 170])  # Circle

    # === 7. Scattered obstacles (add variety) ===
    # Random strategic placements
    obstacles.append([150, 150])  # Circle
    obstacles.append([100, 250])  # Circle
    obstacles.append([550, 450])  # Circle
    obstacles.append([620, 350])  # Circle

    # Triangle obstacles
    obstacles.append([300, 150, 330, 180, 270, 180])
    obstacles.append([450, 480, 480, 510, 420, 510])

    # === 8. Large rectangular obstacles (create zones) ===
    obstacles.append([80, 80, 180, 80, 180, 140, 80, 140])
    obstacles.append([600, 500, 680, 500, 680, 600, 600, 600])

    return start_position, target_position, obstacles


def save_map(map_name: str):
    """Save the challenge map to maps/ directory."""

    start_pos, target_pos, obstacles = create_challenge_map()

    # Create map directory
    maps_dir = Path("maps")
    maps_dir.mkdir(exist_ok=True)

    map_folder = maps_dir / map_name
    map_folder.mkdir(exist_ok=True)

    # Save files
    np.save(map_folder / "start.npy", start_pos)
    np.save(map_folder / "target.npy", target_pos)
    np.save(map_folder / "obstacles.npy", np.array(obstacles, dtype=object), allow_pickle=True)

    print(f"✓ Created map: {map_name}")
    print(f"  Start: {start_pos[0]}")
    print(f"  Target: {target_pos[0]}")
    print(f"  Obstacles: {len(obstacles)}")
    print(f"\nMap features:")
    print(f"  - Narrow corridors and passages")
    print(f"  - Dense obstacle clusters")
    print(f"  - Maze-like structure")
    print(f"  - Strategic guard obstacles near goal")
    print(f"  - Mix of shapes (circles, polygons, rectangles)")
    print(f"\nDifficulty: ⭐⭐⭐⭐⭐ (Advanced)")


if __name__ == "__main__":
    save_map("challenge")
    print(f"\nTo test the map:")
    print(f"  python -m src.main")
    print(f"  (Select 'challenge' from map dropdown)")
    print(f"\nTo train on this map:")
    print(f"  python rl_tui.py")
    print(f"  (Select 'challenge' in training mode)")

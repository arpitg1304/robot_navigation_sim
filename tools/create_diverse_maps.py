#!/usr/bin/env python3
"""
Create 6 diverse navigation maps with varying difficulties and characteristics
to train robust, generalizable RL policies.

Map design philosophy:
- Different obstacle densities (sparse to dense)
- Different obstacle sizes (small to large)
- Different spatial patterns (scattered, clustered, corridors)
- Different navigation strategies required (direct, detour, threading)
"""

import numpy as np
import os

def create_map(name, start, target, obstacles, description, difficulty):
    """Create and save a map with metadata"""
    map_dir = f"maps/{name}"
    os.makedirs(map_dir, exist_ok=True)

    # Convert obstacles from [(x1,y1), (x2,y2)] format to flat polygon format
    # Rectangle corners: bottom-left, top-left, top-right, bottom-right
    formatted_obstacles = []
    for obs in obstacles:
        (x1, y1), (x2, y2) = obs
        # Create rectangle as polygon: [x1,y1, x1,y2, x2,y2, x2,y1]
        formatted_obstacles.append([x1, y1, x1, y2, x2, y2, x2, y1])

    # Save map files in the format expected by Environment class
    # Start and target need to be 2D arrays: [[x, y]]
    np.save(f"{map_dir}/start.npy", np.array([start]))
    np.save(f"{map_dir}/target.npy", np.array([target]))
    np.save(f"{map_dir}/obstacles.npy", np.array(formatted_obstacles, dtype=object), allow_pickle=True)

    # Create README
    readme_content = f"""# {name.replace('_', ' ').title()} Map

**Difficulty:** {difficulty} ⭐
**Description:** {description}

## Layout
- Start: {start}
- Target: {target}
- Obstacles: {len(obstacles)}

## Training Purpose
{get_training_purpose(name)}
"""

    with open(f"{map_dir}/README.md", 'w') as f:
        f.write(readme_content)

    print(f"✓ Created {name} ({difficulty}⭐) - {len(obstacles)} obstacles")

def get_training_purpose(name):
    purposes = {
        'open_field': 'Teaches basic goal-seeking behavior with minimal obstacle avoidance',
        'scattered_rocks': 'Teaches navigation around randomly distributed obstacles',
        'narrow_corridors': 'Teaches precise maneuvering through tight spaces',
        'dense_forest': 'Teaches navigation in cluttered environments with many obstacles',
        'u_shaped_trap': 'Teaches escaping local minima and finding indirect paths',
        'mixed_complexity': 'Combines multiple challenge types for robust learning'
    }
    return purposes.get(name, 'General navigation training')

# Map 1: Open Field (Easy) - Sparse obstacles
# Purpose: Learn basic goal-seeking with minimal interference
obstacles_1 = [
    [(200, 150), (250, 180)],  # Small obstacle mid-field
    [(400, 350), (450, 400)],  # Small obstacle lower right
    [(150, 450), (180, 480)],  # Small obstacle lower left
]

create_map(
    name='open_field',
    start=[100, 100],
    target=[600, 500],
    obstacles=obstacles_1,
    description='Wide open space with only 3 small obstacles. Direct path available.',
    difficulty='1/6 (Easy)'
)

# Map 2: Scattered Rocks (Easy-Medium) - Random distribution
# Purpose: Learn to weave between obstacles
obstacles_2 = [
    [(150, 200), (180, 230)],
    [(300, 150), (340, 190)],
    [(450, 250), (490, 290)],
    [(250, 350), (280, 380)],
    [(400, 450), (430, 480)],
    [(550, 350), (580, 380)],
    [(100, 450), (130, 480)],
    [(500, 100), (530, 130)],
]

create_map(
    name='scattered_rocks',
    start=[50, 50],
    target=[650, 550],
    obstacles=obstacles_2,
    description='Medium-density scattered obstacles. Requires moderate path planning.',
    difficulty='2/6 (Easy-Medium)'
)

# Map 3: Narrow Corridors (Medium) - Precision required
# Purpose: Learn tight maneuvering
obstacles_3 = [
    # Vertical walls creating corridors
    [(200, 100), (220, 400)],
    [(400, 200), (420, 600)],

    # Horizontal segments creating gaps
    [(100, 300), (200, 320)],
    [(420, 350), (600, 370)],

    # Small obstacles in corridors
    [(250, 250), (280, 270)],
    [(450, 450), (480, 470)],
]

create_map(
    name='narrow_corridors',
    start=[50, 150],
    target=[650, 500],
    obstacles=obstacles_3,
    description='Long narrow walls with gaps. Requires threading through corridors.',
    difficulty='3/6 (Medium)'
)

# Map 4: Dense Forest (Medium-Hard) - High obstacle density
# Purpose: Learn navigation in cluttered space
obstacles_4 = [
    [(100, 100), (130, 130)],
    [(180, 100), (210, 130)],
    [(260, 100), (290, 130)],
    [(340, 100), (370, 130)],
    [(420, 100), (450, 130)],
    [(500, 100), (530, 130)],

    [(100, 200), (130, 230)],
    [(200, 200), (230, 230)],
    [(300, 200), (330, 230)],
    [(400, 200), (430, 230)],
    [(500, 200), (530, 230)],
    [(600, 200), (630, 230)],

    [(150, 300), (180, 330)],
    [(250, 300), (280, 330)],
    [(350, 300), (380, 330)],
    [(450, 300), (480, 330)],
    [(550, 300), (580, 330)],

    [(100, 400), (130, 430)],
    [(200, 400), (230, 430)],
    [(300, 400), (330, 430)],
    [(400, 400), (430, 430)],
    [(500, 400), (530, 430)],

    [(150, 500), (180, 530)],
    [(350, 500), (380, 530)],
    [(550, 500), (580, 530)],
]

create_map(
    name='dense_forest',
    start=[50, 550],
    target=[650, 50],
    obstacles=obstacles_4,
    description='Many small obstacles densely packed. Requires careful path planning.',
    difficulty='4/6 (Medium-Hard)'
)

# Map 5: U-Shaped Trap (Hard) - Local minima challenge
# Purpose: Learn to escape traps and find indirect paths
obstacles_5 = [
    # Large U-shape walls
    [(200, 100), (250, 500)],  # Left wall
    [(200, 450), (600, 500)],  # Bottom wall
    [(550, 100), (600, 500)],  # Right wall

    # Additional obstacles inside creating complexity
    [(300, 200), (350, 250)],
    [(450, 200), (500, 250)],
    [(350, 350), (450, 380)],
]

create_map(
    name='u_shaped_trap',
    start=[400, 300],  # Start inside the U
    target=[400, 50],   # Goal outside, requires going around
    obstacles=obstacles_5,
    description='U-shaped walls creating a trap. Requires finding the way out and around.',
    difficulty='5/6 (Hard)'
)

# Map 6: Mixed Complexity (Hard) - Combines multiple challenges
# Purpose: Test all learned skills together
obstacles_6 = [
    # Large central obstacle cluster
    [(250, 250), (350, 350)],
    [(300, 200), (400, 250)],
    [(200, 300), (250, 400)],
    [(350, 300), (450, 350)],

    # Corridor section
    [(100, 100), (120, 300)],
    [(500, 300), (520, 600)],

    # Scattered small obstacles
    [(150, 450), (170, 470)],
    [(450, 150), (470, 170)],
    [(550, 450), (570, 470)],
    [(150, 150), (170, 170)],

    # Narrow passage obstacles
    [(300, 450), (320, 500)],
    [(380, 450), (400, 500)],

    # Wall segments
    [(400, 100), (600, 120)],
    [(100, 500), (200, 520)],
]

create_map(
    name='mixed_complexity',
    start=[50, 50],
    target=[650, 550],
    obstacles=obstacles_6,
    description='Combines clusters, corridors, narrow passages, and scattered obstacles.',
    difficulty='6/6 (Hard)'
)

print("\n" + "="*60)
print("✓ Created 6 diverse maps for generalization training!")
print("="*60)
print("\nMap Summary:")
print("1. open_field       - Sparse, direct path available")
print("2. scattered_rocks  - Medium density, random distribution")
print("3. narrow_corridors - Precision maneuvering required")
print("4. dense_forest     - High density, complex paths")
print("5. u_shaped_trap    - Trap escape, indirect routing")
print("6. mixed_complexity - All challenges combined")
print("\nTo train with all maps, use the TUI and select 'Custom' map selection,")
print("then enter: open_field,scattered_rocks,narrow_corridors,dense_forest,u_shaped_trap,mixed_complexity")
print("\nOr update rl_tui.py to include these maps in the 'All maps' option.")

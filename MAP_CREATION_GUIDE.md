# Map Creation Guide

This guide explains how to create custom maps (environments) for the navigation simulator.

## What is a Map?

A map consists of two components:
1. **Target** - The goal location (single point with radius)
2. **Obstacles** - Circles or polygons that the robot must avoid

## Map Storage Structure

Maps are stored in the `maps/` directory using a **folder-based structure**:
```
maps/
├── my_maze/
│   ├── target.npy
│   └── obstacles.npy
├── corridor/
│   ├── target.npy
│   └── obstacles.npy
└── simple/
    ├── target.npy
    └── obstacles.npy
```

Each map has its own folder containing:
- `target.npy` - Target position data
- `obstacles.npy` - Obstacles data (circles and polygons)

### Migrating Old Maps

If you have maps in the old format (`mapname_target.npy` and `mapname_obstacles.npy`), run the migration script:

```bash
python migrate_maps.py
```

This will automatically convert all old-format maps to the new folder structure.

## Quick Start - Interactive Map Editor

### Using the Built-in Map Editor

```bash
# Run the interactive map editor
python -m tools.map_editor
```

The map editor provides:
- **Click and drag** to create circular obstacles (radius based on drag distance)
- **Polygon mode** to create custom polygonal obstacles
- **Right-click** to place the target
- **Delete key** to remove selected obstacle
- **Save/Load** functionality for map files
- **Clear** button to start fresh

### Controls

**Circle Mode (Default):**
- **Left Click + Drag**: Create circular obstacle (drag distance = visual preview of size)
- Note: All circles have radius 45px in simulator, drag just shows preview

**Polygon Mode:**
- **P**: Enter polygon mode
- **Left Click**: Add vertex to polygon
- **Enter**: Complete polygon (needs 3+ vertices)
- **ESC**: Cancel polygon mode

**General:**
- **Right Click**: Place target
- **Click obstacle + Delete**: Remove selected obstacle
- **N**: Edit map name (type name and press Enter)
- **S**: Save map (saves with current map name)
- **L**: Load map (loads map with current name)
- **C**: Clear all obstacles
- **ESC**: Cancel polygon mode / name editing / Quit editor

---

## Manual Map Creation

### Method 1: Python Script (Recommended)

Create a Python script to generate your map:

```python
import numpy as np
from pathlib import Path

# Define target (x, y)
target = np.array([[500, 500]])

# Define obstacles
obstacles = [
    # Circles: [x, y]
    [150, 150],
    [300, 200],
    [450, 350],

    # Polygons: [x1, y1, x2, y2, x3, y3, ...]
    [100, 400, 200, 400, 200, 500, 100, 500],  # Rectangle
    [550, 100, 600, 150, 550, 200],            # Triangle
]

# Save to files
maps_dir = Path("maps")
maps_dir.mkdir(exist_ok=True)

np.save(maps_dir / "my_target.npy", target)
np.save(maps_dir / "my_obstacles.npy", obstacles, allow_pickle=True)

print("Map saved to maps/")
```

### Method 2: Interactive Python Console

```python
import numpy as np

# Start with empty lists
target = [[350, 600]]  # [x, y]
obstacles = []

# Add circular obstacles (just x, y - radius is set in config)
obstacles.append([200, 200])
obstacles.append([400, 300])
obstacles.append([500, 450])

# Add polygon obstacles (list of x,y coordinates)
# Rectangle at (100, 100) to (200, 200)
obstacles.append([100, 100, 200, 100, 200, 200, 100, 200])

# Save
np.save("maps/target.npy", target)
np.save("maps/obstacles.npy", obstacles, allow_pickle=True)
```

---

## Map File Format

Maps are stored as NumPy `.npy` files in their own folders:

### Target File (`maps/my_map/target.npy`)
```python
# Format: [[x, y]]
np.array([[500, 500]])  # Single target at (500, 500)
```

### Obstacles File (`maps/my_map/obstacles.npy`)
```python
# List of obstacles (circles and polygons mixed)
obstacles = [
    [150, 150],                              # Circle at (150, 150)
    [300, 200],                              # Circle at (300, 200)
    [100, 400, 200, 400, 200, 500, 100, 500], # Polygon (rectangle)
]

np.save("obstacles.npy", obstacles, allow_pickle=True)
```

### Distinguishing Circles vs Polygons

The code automatically detects:
- **Circle**: Array with 2 elements `[x, y]`
- **Polygon**: Array with 4+ elements `[x1, y1, x2, y2, ...]`

---

## Common Map Patterns

### 1. Maze Map

```python
import numpy as np

target = [[650, 650]]

obstacles = [
    # Vertical walls
    [200, 0, 200, 300],
    [200, 400, 200, 700],
    [400, 0, 400, 300],
    [400, 400, 400, 700],

    # Horizontal walls
    [0, 200, 300, 200],
    [400, 200, 700, 200],
    [0, 500, 300, 500],
    [400, 500, 700, 500],
]

# Convert to polygon format
obstacles = [[x1, y1, x2, y2, x2+10, y2+10, x1+10, y1+10]
             for x1, y1, x2, y2 in obstacles]

np.save("maps/maze_target.npy", target)
np.save("maps/maze_obstacles.npy", obstacles, allow_pickle=True)
```

### 2. Random Scattered Obstacles

```python
import numpy as np

target = [[600, 600]]

# Generate 15 random circular obstacles
np.random.seed(42)
obstacles = []
for _ in range(15):
    x = np.random.randint(100, 600)
    y = np.random.randint(100, 600)
    # Avoid placing too close to target
    if (x - 600)**2 + (y - 600)**2 > 10000:
        obstacles.append([x, y])

np.save("maps/random_target.npy", target)
np.save("maps/random_obstacles.npy", obstacles, allow_pickle=True)
```

### 3. Corridor Map

```python
import numpy as np

target = [[650, 350]]

obstacles = [
    # Top wall
    [0, 250, 500, 250, 500, 260, 0, 260],
    # Bottom wall
    [0, 440, 500, 440, 500, 450, 0, 450],
    # Obstacles in corridor
    [200, 320],
    [350, 360],
]

np.save("maps/corridor_target.npy", target)
np.save("maps/corridor_obstacles.npy", obstacles, allow_pickle=True)
```

### 4. Open Space with Central Obstacle

```python
import numpy as np

target = [[600, 600]]

obstacles = [
    # Large central obstacle
    [350, 350],  # Circle
]

np.save("maps/simple_target.npy", target)
np.save("maps/simple_obstacles.npy", obstacles, allow_pickle=True)
```

---

## Loading Custom Maps

### Built-in Map Selector (Recommended)

The simulator now includes a **map dropdown selector** in the UI:

1. Create your map using the map editor (press **N** to set name, press **S** to save)
2. Run the simulator: `python -m src.main`
3. Use the **Map dropdown** in the right panel to select your map
4. The simulator will automatically load and display your map

Maps are automatically detected from the `maps/` directory and shown in the dropdown.

### Programmatic Loading

You can also load maps programmatically:

```python
from src.environment import Environment

env = Environment()

# Load a specific map by name
env.load_map("my_maze")  # Loads from maps/my_maze/

# Get list of available maps
available_maps = Environment.get_available_maps()
print(f"Available maps: {available_maps}")
```

---

## Map Specifications

### Canvas Size
- Width: 700 pixels
- Height: 700 pixels
- Coordinate system: (0, 0) is top-left

### Safe Zones
- Keep obstacles away from edges (10px margin)
- Don't place obstacles at robot start position (350, 200)
- Ensure target is reachable

### Obstacle Sizes
- Circle radius: 45 pixels (configurable in config.py)
- Polygon: Any size (define all vertices)

### Target
- Radius: 25 pixels (configurable)
- Detection distance: 20 pixels (configurable)

---

## Validation

### Check if Map is Valid

```python
def validate_map(target_file, obstacles_file):
    """Validate a map file."""
    import numpy as np

    # Load files
    target = np.load(target_file, allow_pickle=True)
    obstacles = np.load(obstacles_file, allow_pickle=True)

    # Check target
    assert len(target) > 0, "No target defined"
    assert len(target[0]) == 2, "Target must be [x, y]"
    assert 0 <= target[0][0] <= 700, "Target x out of bounds"
    assert 0 <= target[0][1] <= 700, "Target y out of bounds"

    # Check obstacles
    for i, obs in enumerate(obstacles):
        if len(obs) == 2:  # Circle
            assert 0 <= obs[0] <= 700, f"Obstacle {i} x out of bounds"
            assert 0 <= obs[1] <= 700, f"Obstacle {i} y out of bounds"
        elif len(obs) >= 4:  # Polygon
            assert len(obs) % 2 == 0, f"Obstacle {i} has odd number of coords"
            for j in range(0, len(obs), 2):
                assert 0 <= obs[j] <= 700, f"Obstacle {i} point {j//2} x out of bounds"
                assert 0 <= obs[j+1] <= 700, f"Obstacle {i} point {j//2} y out of bounds"

    print("✓ Map is valid!")
    return True

# Usage
validate_map("maps/my_target.npy", "maps/my_obstacles.npy")
```

---

## Map Templates

### Empty Map
```python
target = [[600, 600]]
obstacles = []
```

### Single Obstacle
```python
target = [[600, 600]]
obstacles = [[350, 350]]  # One circle in the middle
```

### Wall Following Test
```python
target = [[650, 650]]
obstacles = [
    # U-shaped wall
    [100, 100, 600, 100, 600, 110, 100, 110],  # Top
    [100, 100, 110, 600, 100, 600],             # Left
    [600, 100, 610, 600, 600, 600],             # Right
]
```

---

## Tips for Good Maps

1. **Start Simple**: Begin with 1-3 obstacles
2. **Test Reachability**: Ensure target is reachable
3. **Avoid Traps**: Don't create dead-ends (unless testing)
4. **Vary Difficulty**: Create easy, medium, hard versions
5. **Name Clearly**: Use descriptive filenames
6. **Document**: Add comments in creation script

### Difficulty Guidelines

**Easy:**
- 1-3 obstacles
- Clear path to target
- Wide open spaces

**Medium:**
- 5-10 obstacles
- Some path planning required
- Mix of circles and polygons

**Hard:**
- 10+ obstacles
- Narrow passages
- Multiple dead-ends
- Maze-like structure

---

## Sharing Maps

To share your map:

1. **Include both files**:
   - `my_map_target.npy`
   - `my_map_obstacles.npy`

2. **Add a preview image** (optional)

3. **Document**:
   ```markdown
   ## My Awesome Map

   Difficulty: Medium
   Obstacles: 8 circles, 3 polygons
   Best Algorithm: Reactive Target-Centric

   Features:
   - Narrow corridor
   - Central maze section
   - Multiple paths to target
   ```

4. **Share creation script** (optional but helpful)

---

## Troubleshooting

**Q: My map doesn't load**
- Check file names match exactly
- Verify files are in `maps/` directory
- Ensure proper NumPy format

**Q: Obstacles don't appear**
- Check coordinates are within (0-700, 0-700)
- Verify array format (circles need 2 values, polygons need 4+)
- Check `allow_pickle=True` when saving

**Q: Robot starts inside obstacle**
- Don't place obstacles at (350, 200)
- Leave 50px clearance around start position

**Q: Target is unreachable**
- Verify path exists from start to target
- Check obstacles don't completely block access

---

## Advanced: Procedural Generation

Generate maps programmatically:

```python
import numpy as np
import random

def generate_random_map(num_obstacles=10):
    """Generate a random map."""
    # Target in bottom-right
    target = [[600, 600]]

    obstacles = []
    for _ in range(num_obstacles):
        # Random position (avoid start and target)
        while True:
            x = random.randint(100, 600)
            y = random.randint(100, 600)

            # Check distance from start
            if (x - 350)**2 + (y - 200)**2 < 5000:
                continue
            # Check distance from target
            if (x - 600)**2 + (y - 600)**2 < 5000:
                continue

            obstacles.append([x, y])
            break

    return target, obstacles

# Generate and save
target, obstacles = generate_random_map(15)
np.save("maps/random_target.npy", target)
np.save("maps/random_obstacles.npy", obstacles, allow_pickle=True)
```

---

## Next Steps

1. **Create your first map** using a Python script
2. **Test it** in the simulator
3. **Iterate** - adjust based on robot behavior
4. **Share** your best maps with others!

For the interactive map editor tool, see [tools/map_editor.py](tools/map_editor.py).

Happy map making! 🗺️

---

## Previewing Existing Maps

### Quick Preview

Preview any map without running the full simulator:

```bash
python tools/preview_map.py <map_name>
```

**Example:**
```bash
# Preview a map called "maze"
python tools/preview_map.py maze

# This will load from:
#   maps/maze/target.npy
#   maps/maze/obstacles.npy
```

### List All Maps

See all available maps:

```bash
# Method 1: Using preview tool
python tools/preview_map.py

# Method 2: Using list script
python list_maps.py

# Method 3: Using shell script (Linux/Mac)
./preview_all_maps.sh
```

### Preview Features

The preview window shows:
- **Canvas background** with grid (700x700)
- **Obstacles** (circles and polygons)
- **Target** (glowing amber circle)
- **Robot start position** (blue circle at 350, 200)
- **Info bar** with map name, obstacle count, target position

**Controls:**
- `ESC` - Close preview window

### Batch Preview

Preview a map from the list:

```bash
# List and preview in one command
python list_maps.py maze
```

### Example Session

```bash
$ python list_maps.py

============================================================
Available Maps
============================================================
  • corridor
  • custom_map
  • maze
  • simple
  • test_map

Total maps: 5

Commands:
  Preview: python tools/preview_map.py <map_name>
  Edit:    python -m tools.map_editor
  Create:  python tools/create_map.py

$ python tools/preview_map.py maze

============================================================
Map Preview: maze
============================================================
Target: (650.0, 650.0)
Obstacles: 12

Obstacle details:
  0: Circle at (150.0, 150.0)
  1: Circle at (300.0, 200.0)
  2: Polygon with 4 vertices
  3: Polygon with 4 vertices
  4: Circle at (450.0, 350.0)
  ...

Press ESC to close preview
============================================================

[Preview window opens]
```

### Tips

1. **Before testing**: Always preview maps before running in simulator
2. **Check reachability**: Verify target is reachable from start (350, 200)
3. **Obstacle placement**: Ensure obstacles aren't blocking the only path
4. **Quick iteration**: Make changes in editor, save, preview, repeat

---

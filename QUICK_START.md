# Quick Start Guide

## Running the Simulator

```bash
cd reactive-nav-sim-modern
python -m src.main
```

## Available Algorithms (Click "Change Algorithm" to cycle)

1. **Reactive Navigation (Random)** - Randomly picks safe directions
2. **Reactive Navigation (Target-Centric)** - Picks safe direction closest to target ⭐ DEFAULT
3. **Simple Target Seeking** - Direct path to target (no obstacle avoidance)
4. **Wall Follower** - Right-hand rule for maze solving
5. **Potential Field** - Attraction/repulsion force-based navigation

## Create Your Own Algorithm in 3 Steps

### Step 1: Copy the template

```bash
cp user_algorithms/template.py user_algorithms/my_algorithm.py
```

### Step 2: Edit the file

```python
# user_algorithms/my_algorithm.py
from src.algorithms.base import NavigationAlgorithm
import math

class MyAlgorithm(NavigationAlgorithm):
    def get_name(self):
        return "My Cool Algorithm"

    def compute_direction(self, robot_x, robot_y, robot_radius,
                         robot_heading, environment, sonar):
        # Your logic here
        dx = environment.target.x - robot_x
        dy = environment.target.y - robot_y
        angle = math.degrees(math.atan2(dy, dx))
        return round(angle / 45) * 45 % 360
```

### Step 3: Register it

Edit `src/main.py`, add at the top:
```python
from user_algorithms.my_algorithm import MyAlgorithm
```

Then add to the algorithms list (around line 35):
```python
self.algorithms = [
    ReactiveNavigationAlgorithm(target_centric=False),
    ReactiveNavigationAlgorithm(target_centric=True),
    SimpleTargetSeekingAlgorithm(),
    WallFollowerAlgorithm(),
    PotentialFieldAlgorithm(),
    MyAlgorithm(),  # Add your algorithm here!
]
```

Run the simulator and click "Change Algorithm" until you see yours!

## What You Can Access

### Environment
- `environment.target.x`, `environment.target.y` - Target position
- `environment.obstacles` - List of obstacles
- `environment.check_collision(x, y, margin)` - Check if position is safe
- `environment.is_path_clear(x1, y1, x2, y2, margin)` - Check if path is clear

### Sonar (if enabled)
```python
if sonar:
    sonar.sweep(robot_x, robot_y, environment,
               target_centric=False, robot_radius=robot_radius)
    safe_directions = sonar.allowed_directions  # List like [0, 45, 90, ...]
```

### Return Value
- Return angle in degrees: 0°=East, 90°=North, 180°=West, 270°=South
- Snap to 45° increments: 0, 45, 90, 135, 180, 225, 270, 315

## Need More Help?

See **[ALGORITHM_GUIDE.md](ALGORITHM_GUIDE.md)** for the complete guide with examples!

## Tips

- Print debug info: `print(f"Moving {angle}°")`
- Check for None: `if sonar is not None:`
- Normalize angles: `angle = angle % 360`
- Use math.atan2: `angle = math.atan2(dy, dx)` (note: dy first!)

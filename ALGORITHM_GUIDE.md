# Navigation Algorithm Development Guide

This guide shows you how to create your own custom navigation algorithms for the simulator.

## Quick Start

### 1. Create Your Algorithm File

Create a new Python file in `src/algorithms/` or `user_algorithms/`:

```python
# src/algorithms/my_algorithm.py or user_algorithms/my_algorithm.py
from src.algorithms.base import NavigationAlgorithm
from src.environment import Environment
from typing import Optional
import math

class MyCustomAlgorithm(NavigationAlgorithm):
    """Your custom navigation algorithm."""

    def get_name(self) -> str:
        return "My Custom Algorithm"

    def get_description(self) -> str:
        return "Description of what your algorithm does"

    def compute_direction(
        self,
        robot_x: float,
        robot_y: float,
        robot_radius: float,
        robot_heading: float,
        environment: Environment,
        sonar: Optional[object] = None,
    ) -> float:
        """
        Compute the direction the robot should move.

        Returns:
            Angle in degrees (0°=East, 90°=North, 180°=West, 270°=South)
        """
        # Your algorithm logic here
        # Example: move toward target
        dx = environment.target.x - robot_x
        dy = environment.target.y - robot_y
        angle = math.degrees(math.atan2(dy, dx))
        return angle % 360
```

### 2. Register Your Algorithm

Add your algorithm to `src/main.py`:

```python
from src.algorithms.my_algorithm import MyCustomAlgorithm

class Simulator:
    def __init__(self) -> None:
        # ... existing code ...

        self.algorithms = [
            ReactiveNavigationAlgorithm(target_centric=False),
            ReactiveNavigationAlgorithm(target_centric=True),
            SimpleTargetSeekingAlgorithm(),
            WallFollowerAlgorithm(),
            PotentialFieldAlgorithm(),
            MyCustomAlgorithm(),  # Add your algorithm here!
        ]
```

### 3. Run the Simulator

```bash
python -m src.main
```

Click "Change Algorithm" to cycle through and select your algorithm!

---

## API Reference

### NavigationAlgorithm Base Class

All custom algorithms must inherit from `NavigationAlgorithm` and implement `compute_direction()`.

#### Required Method

##### `compute_direction(robot_x, robot_y, robot_radius, robot_heading, environment, sonar) -> float`

Computes the direction the robot should move.

**Parameters:**
- `robot_x` (float): Current X position of the robot
- `robot_y` (float): Current Y position of the robot
- `robot_radius` (float): Radius of the robot (for collision checking)
- `robot_heading` (float): Current heading in degrees
- `environment` (Environment): Environment object with obstacles and target
- `sonar` (Optional[object]): Sonar sensor object (None if sonar disabled)

**Returns:**
- `float`: Angle in degrees where:
  - 0° = East (right)
  - 90° = North (up)
  - 180° = West (left)
  - 270° = South (down)

**Important:** Return angles are snapped to 45° increments (0, 45, 90, 135, 180, 225, 270, 315)

#### Optional Methods

##### `get_name() -> str`
Returns the display name for your algorithm.

##### `get_description() -> str`
Returns a brief description of how your algorithm works.

##### `reset() -> None`
Called when the simulation restarts. Override this if your algorithm maintains state.

##### `on_collision() -> None`
Called when the robot collides with an obstacle.

##### `on_target_reached() -> None`
Called when the robot reaches the target.

---

## Environment API

The `environment` parameter provides access to:

### Target

```python
environment.target.x       # Target X position
environment.target.y       # Target Y position
environment.target.radius  # Target radius
```

### Obstacles

```python
for obstacle in environment.obstacles:
    if isinstance(obstacle, Circle):
        x, y = obstacle.x, obstacle.y
        radius = obstacle.radius
        distance = obstacle.distance_to(robot_x, robot_y)
    elif isinstance(obstacle, Polygon):
        points = obstacle.points  # List of (x, y) tuples
```

### Collision Detection

```python
# Check if a position would collide
is_colliding = environment.check_collision(x, y, robot_radius)

# Check if a path is clear
is_clear = environment.is_path_clear(x1, y1, x2, y2, robot_radius)
```

---

## Sonar API

If `sonar` is provided (when sonar is enabled):

```python
# Perform a sweep and get safe directions
angle = sonar.sweep(robot_x, robot_y, environment,
                   target_centric=False, robot_radius=robot_radius)

# Access safe directions after sweep
safe_directions = sonar.allowed_directions  # List of angles (0, 45, 90, etc.)

# Access sonar configuration
sonar_range = sonar.range  # Detection range (default: 60)
angles = sonar.angles      # Beam angles [0, 45, 90, 135, 180, 225, 270, 315]
```

---

## Example Algorithms

### Example 1: Simple Target Seeking

Always move directly toward the target (no obstacle avoidance):

```python
def compute_direction(self, robot_x, robot_y, robot_radius, robot_heading,
                     environment, sonar):
    dx = environment.target.x - robot_x
    dy = environment.target.y - robot_y
    angle = math.degrees(math.atan2(dy, dx))

    # Snap to nearest 45° angle
    angle = round(angle / 45) * 45
    return angle % 360
```

### Example 2: Using Sonar for Obstacle Avoidance

```python
def compute_direction(self, robot_x, robot_y, robot_radius, robot_heading,
                     environment, sonar):
    if sonar is None:
        # Fallback if no sonar
        return robot_heading

    # Get safe directions
    sonar.sweep(robot_x, robot_y, environment,
               target_centric=False, robot_radius=robot_radius)

    if sonar.allowed_directions:
        # Pick a random safe direction
        import random
        return random.choice(sonar.allowed_directions)
    else:
        # No safe directions, turn around
        return (robot_heading + 180) % 360
```

### Example 3: Stateful Algorithm

```python
class MemoryAlgorithm(NavigationAlgorithm):
    def __init__(self):
        super().__init__()
        self.visited_positions = []
        self.stuck_count = 0

    def reset(self):
        """Clear state when simulation restarts."""
        self.visited_positions = []
        self.stuck_count = 0

    def compute_direction(self, robot_x, robot_y, robot_radius, robot_heading,
                         environment, sonar):
        # Remember where we've been
        self.visited_positions.append((robot_x, robot_y))

        # Your algorithm logic using historical data
        # ...

        return angle

    def on_collision(self):
        """React to collisions."""
        self.stuck_count += 1
        if self.stuck_count > 5:
            # Take special action if stuck
            pass
```

### Example 4: Potential Field

```python
def compute_direction(self, robot_x, robot_y, robot_radius, robot_heading,
                     environment, sonar):
    # Attractive force toward target
    target_dx = environment.target.x - robot_x
    target_dy = environment.target.y - robot_y
    target_dist = math.sqrt(target_dx**2 + target_dy**2)

    attractive_fx = target_dx / target_dist if target_dist > 0 else 0
    attractive_fy = target_dy / target_dist if target_dist > 0 else 0

    # Repulsive forces from obstacles
    repulsive_fx = 0.0
    repulsive_fy = 0.0

    for obstacle in environment.obstacles:
        if hasattr(obstacle, 'distance_to'):  # Circle
            obs_dist = obstacle.distance_to(robot_x, robot_y)
            obs_x, obs_y = obstacle.x, obstacle.y

            if obs_dist < 100 and obs_dist > 0:  # Influence distance
                repulsion = 50.0 / (obs_dist ** 2)
                dx = (robot_x - obs_x) / obs_dist
                dy = (robot_y - obs_y) / obs_dist
                repulsive_fx += repulsion * dx
                repulsive_fy += repulsion * dy

    # Combine forces
    total_fx = attractive_fx + repulsive_fx
    total_fy = attractive_fy + repulsive_fy

    angle = math.degrees(math.atan2(total_fy, total_fx))
    angle = round(angle / 45) * 45
    return angle % 360
```

---

## Tips & Best Practices

### 1. Always Handle Edge Cases
```python
# Check for division by zero
if distance > 0:
    dx = dx / distance
    dy = dy / distance

# Check if sonar is available
if sonar is not None:
    angle = sonar.sweep(...)
else:
    # Fallback behavior
    angle = some_default_value
```

### 2. Snap Angles to 45° Increments

The robot can only move in 8 directions:

```python
def snap_angle(angle):
    """Snap to nearest 45° increment."""
    return round(angle / 45) * 45
```

### 3. Test Collision Before Moving

The simulator automatically checks collisions, but you can do it yourself:

```python
# Check if proposed direction is safe
new_x = robot_x + 20 * math.cos(math.radians(angle))
new_y = robot_y + 20 * math.sin(math.radians(angle))

if not environment.check_collision(new_x, new_y, robot_radius):
    return angle
else:
    # Try alternative direction
    return alternative_angle
```

### 4. Use Debug Printing

```python
def compute_direction(self, ...):
    angle = # your calculation
    print(f"Robot at ({robot_x:.1f}, {robot_y:.1f}), moving {angle}°")
    return angle
```

### 5. Consider Performance

The `compute_direction` method is called every few frames. Keep it efficient:

```python
# ❌ Bad: Creating large data structures every call
def compute_direction(self, ...):
    all_paths = compute_all_possible_paths()  # Expensive!

# ✅ Good: Cache or precompute when possible
def __init__(self):
    self.cached_data = precompute_expensive_stuff()
```

---

## Advanced Topics

### Custom Parameters

```python
class ConfigurableAlgorithm(NavigationAlgorithm):
    def __init__(self, speed_factor=1.0, aggression=0.5):
        super().__init__()
        self.speed_factor = speed_factor
        self.aggression = aggression

    def get_name(self):
        return f"Custom (aggression={self.aggression})"
```

Register multiple instances with different parameters:

```python
self.algorithms = [
    ConfigurableAlgorithm(aggression=0.2),
    ConfigurableAlgorithm(aggression=0.8),
]
```

### Path Planning Algorithms

You can implement more sophisticated algorithms like A*, RRT, or D*:

```python
class AStarAlgorithm(NavigationAlgorithm):
    def __init__(self):
        super().__init__()
        self.planned_path = []
        self.current_waypoint_idx = 0

    def compute_direction(self, robot_x, robot_y, robot_radius, robot_heading,
                         environment, sonar):
        # Replan if needed
        if not self.planned_path or self.needs_replanning(robot_x, robot_y):
            self.planned_path = self.plan_astar(
                (robot_x, robot_y),
                (environment.target.x, environment.target.y),
                environment
            )
            self.current_waypoint_idx = 0

        # Follow the path
        if self.current_waypoint_idx < len(self.planned_path):
            waypoint = self.planned_path[self.current_waypoint_idx]
            dx = waypoint[0] - robot_x
            dy = waypoint[1] - robot_y

            # Move to next waypoint if close enough
            if math.sqrt(dx**2 + dy**2) < 20:
                self.current_waypoint_idx += 1

            angle = math.degrees(math.atan2(dy, dx))
            return round(angle / 45) * 45 % 360

        return robot_heading
```

---

## Troubleshooting

**Q: My algorithm doesn't move toward the target**
- Check that your angle calculation is correct
- Make sure you're using `math.atan2(dy, dx)` not `atan2(dx, dy)`
- Verify angles are in degrees, not radians

**Q: Robot gets stuck in corners**
- Add randomness or exploration behavior
- Implement backtracking when no progress is made
- Use the `on_collision()` callback to adjust strategy

**Q: My algorithm causes crashes**
- Check for division by zero
- Ensure `compute_direction()` always returns a float
- Handle cases where sonar is None

**Q: How do I debug my algorithm?**
```python
def compute_direction(self, ...):
    angle = # your calculation

    # Print debug info
    print(f"Position: ({robot_x:.1f}, {robot_y:.1f})")
    print(f"Target: ({environment.target.x}, {environment.target.y})")
    print(f"Computed angle: {angle}")

    return angle
```

---

## Contributing Your Algorithm

If you create an interesting algorithm, consider sharing it:

1. Add it to `src/algorithms/`
2. Update `src/algorithms/__init__.py`
3. Add an example to this guide
4. Submit a pull request!

---

## Additional Resources

- See existing algorithms in `src/algorithms/` for complete examples
- The simulator uses Pygame for rendering
- Robot step size is 20 pixels (configurable in `src/config.py`)
- Sonar range is 60 pixels (configurable)

Happy algorithm developing!

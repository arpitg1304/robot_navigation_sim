"""Environment module containing obstacles and targets."""

from dataclasses import dataclass
from typing import List, Tuple, Union
import math
import numpy as np
from pathlib import Path


@dataclass
class Circle:
    """Represents a circular obstacle or target."""

    x: float
    y: float
    radius: float

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside this circle."""
        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= self.radius

    def distance_to(self, x: float, y: float) -> float:
        """Calculate distance from a point to the circle's center."""
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


@dataclass
class Polygon:
    """Represents a polygon obstacle."""

    points: List[Tuple[float, float]]

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside this polygon using ray casting."""
        n = len(self.points)
        inside = False

        p1x, p1y = self.points[0]
        for i in range(1, n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside


class Environment:
    """Manages the simulation environment including obstacles and target."""

    def __init__(self) -> None:
        self.obstacles: List[Union[Circle, Polygon]] = []
        self.target: Circle = Circle(0, 0, 0)
        self.walls: List[Polygon] = []
        self._create_boundary_walls()

    def _create_boundary_walls(self) -> None:
        """Create the boundary walls of the environment."""
        # Top wall
        self.walls.append(Polygon([(0, 0), (700, 0), (700, 10), (0, 10)]))
        # Left wall
        self.walls.append(Polygon([(0, 0), (10, 0), (10, 700), (0, 700)]))
        # Bottom wall
        self.walls.append(Polygon([(0, 690), (700, 690), (700, 700), (0, 700)]))
        # Right wall
        self.walls.append(Polygon([(690, 0), (700, 0), (700, 700), (690, 700)]))

    def load_map(self, map_name: str) -> bool:
        """Load a map from the maps directory using folder structure.

        Args:
            map_name: Name of the map folder in maps/

        Returns:
            True if loaded successfully, False otherwise
        """
        maps_dir = Path("maps")
        map_folder = maps_dir / map_name
        target_file = map_folder / "target.npy"
        obstacles_file = map_folder / "obstacles.npy"

        if not target_file.exists() or not obstacles_file.exists():
            print(f"Warning: Map '{map_name}' not found at {map_folder}/")
            return False

        return self.load_from_numpy(str(target_file), str(obstacles_file))

    @staticmethod
    def get_available_maps() -> List[str]:
        """Get list of available map names from maps directory.

        Returns:
            List of map names (folder names that contain valid maps)
        """
        maps_dir = Path("maps")
        if not maps_dir.exists():
            return []

        maps = []
        for map_folder in maps_dir.iterdir():
            if map_folder.is_dir():
                target_file = map_folder / "target.npy"
                obstacles_file = map_folder / "obstacles.npy"
                if target_file.exists() and obstacles_file.exists():
                    maps.append(map_folder.name)

        return sorted(maps)

    def load_from_numpy(self, target_file: str, obstacles_file: str) -> bool:
        """Load environment from numpy files (legacy format support).

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            target_data = np.load(target_file, allow_pickle=True)
            if len(target_data) > 0:
                self.target = Circle(
                    float(target_data[0][0]), float(target_data[0][1]), 25.0
                )
        except Exception as e:
            print(f"Warning: Could not load target file: {e}")
            self.target = Circle(600.0, 600.0, 25.0)
            return False

        try:
            obstacle_data = np.load(obstacles_file, allow_pickle=True)
            self.obstacles.clear()

            for obstacle in obstacle_data:
                if len(obstacle) == 2:
                    # It's a circle (just x, y coordinates)
                    self.obstacles.append(Circle(float(obstacle[0]), float(obstacle[1]), 45.0))
                else:
                    # It's a polygon (list of points)
                    points = [(float(obstacle[i]), float(obstacle[i + 1]))
                             for i in range(0, len(obstacle), 2)]
                    self.obstacles.append(Polygon(points))
            return True
        except Exception as e:
            print(f"Warning: Could not load obstacles file: {e}")
            return False

    def check_collision(self, x: float, y: float, safety_margin: float = 0) -> bool:
        """
        Check if a point collides with any obstacle or wall.

        Args:
            x: X coordinate to check
            y: Y coordinate to check
            safety_margin: Additional distance to maintain from obstacles (e.g., robot radius)
        """
        # Check walls
        for wall in self.walls:
            if wall.contains_point(x, y):
                return True

        # Check obstacles with safety margin
        for obstacle in self.obstacles:
            if isinstance(obstacle, Circle):
                # For circles, check if distance to center is less than obstacle radius + margin
                distance = obstacle.distance_to(x, y)
                if distance <= obstacle.radius + safety_margin:
                    return True
            elif isinstance(obstacle, Polygon):
                # For polygons, check point containment (approximate with margin)
                if obstacle.contains_point(x, y):
                    return True
                # Also check if we're too close to edges (simplified check)
                if safety_margin > 0:
                    # Sample points around the position in a circle of safety_margin radius
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle)
                        test_x = x + safety_margin * math.cos(rad)
                        test_y = y + safety_margin * math.sin(rad)
                        if obstacle.contains_point(test_x, test_y):
                            return True

        return False

    def is_path_clear(self, x1: float, y1: float, x2: float, y2: float, safety_margin: float = 0) -> bool:
        """
        Check if a straight line path is clear of obstacles.

        Args:
            x1, y1: Start position
            x2, y2: End position
            safety_margin: Additional distance to maintain from obstacles (e.g., robot radius)
        """
        # Sample points along the line
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            if self.check_collision(x, y, safety_margin):
                return False
        return True

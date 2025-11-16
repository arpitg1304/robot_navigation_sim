"""Wall-following navigation algorithm."""

import math
from typing import Optional
from .base import NavigationAlgorithm
from src.environment import Environment


class WallFollowerAlgorithm(NavigationAlgorithm):
    """
    Wall-following algorithm (right-hand rule).

    This algorithm follows the right wall to navigate around obstacles.
    It's a classic maze-solving algorithm that works well in simple environments.
    """

    def __init__(self):
        """Initialize wall follower algorithm."""
        super().__init__()
        self.preferred_order = [0, 315, 270, 225, 180, 135, 90, 45]  # Right-priority

    def get_name(self) -> str:
        """Get the algorithm name."""
        return "Wall Follower (Right-Hand Rule)"

    def get_description(self) -> str:
        """Get the algorithm description."""
        return "Follows the right wall to navigate around obstacles"

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
        Compute direction using right-hand wall following.

        Args:
            robot_x: Robot X position
            robot_y: Robot Y position
            robot_radius: Robot radius
            robot_heading: Current heading
            environment: Environment with obstacles
            sonar: Sonar sensor object

        Returns:
            Angle in degrees following the right wall
        """
        if sonar is None:
            # Fallback without sonar
            return robot_heading

        # Get safe directions from sonar
        sonar.sweep(robot_x, robot_y, environment,
                   target_centric=False, robot_radius=robot_radius)

        allowed_directions = sonar.allowed_directions

        if not allowed_directions:
            # No safe directions, turn around
            return (robot_heading + 180) % 360

        # Normalize current heading to sonar angles
        current_heading_normalized = round(robot_heading / 45) * 45

        # Priority: right, forward, left, backward
        # Relative to current heading
        priority_offsets = [-90, 0, 90, -45, 45, -135, 135, 180]

        for offset in priority_offsets:
            candidate = (current_heading_normalized + offset) % 360
            if candidate in allowed_directions:
                return candidate

        # Fallback: pick any safe direction
        import random
        return random.choice(allowed_directions)

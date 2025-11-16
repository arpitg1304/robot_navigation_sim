"""Simple target-seeking algorithm (no obstacle avoidance)."""

import math
from typing import Optional
from .base import NavigationAlgorithm
from src.environment import Environment


class SimpleTargetSeekingAlgorithm(NavigationAlgorithm):
    """
    Simple algorithm that always moves directly toward the target.

    Warning: This algorithm does not avoid obstacles!
    Use this as a baseline to compare against smarter algorithms.
    """

    def get_name(self) -> str:
        """Get the algorithm name."""
        return "Simple Target Seeking"

    def get_description(self) -> str:
        """Get the algorithm description."""
        return "Always moves directly toward target (no obstacle avoidance)"

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
        Compute direction directly toward target.

        Args:
            robot_x: Robot X position
            robot_y: Robot Y position
            robot_radius: Robot radius (not used)
            robot_heading: Current heading (not used)
            environment: Environment with target
            sonar: Sonar sensor (not used)

        Returns:
            Angle in degrees directly toward target
        """
        # Calculate angle to target
        dx = environment.target.x - robot_x
        dy = environment.target.y - robot_y

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Normalize to 0-360
        if angle_deg < 0:
            angle_deg += 360

        # Snap to nearest 45-degree angle (to match sonar directions)
        angle_deg = round(angle_deg / 45) * 45

        return angle_deg % 360

"""Reactive navigation algorithm using sonar."""

import math
import random
from typing import Optional
from .base import NavigationAlgorithm
from src.environment import Environment


class ReactiveNavigationAlgorithm(NavigationAlgorithm):
    """
    Reactive navigation using sonar sensor.

    This algorithm:
    1. Casts sonar beams in 8 directions
    2. Identifies safe (obstacle-free) directions
    3. If target_centric mode: picks the safe direction closest to target
    4. Otherwise: randomly picks a safe direction
    """

    def __init__(self, target_centric: bool = False):
        """
        Initialize reactive navigation algorithm.

        Args:
            target_centric: If True, prefer directions toward the target
        """
        super().__init__()
        self.target_centric = target_centric

    def get_name(self) -> str:
        """Get the algorithm name."""
        suffix = " (Target-Centric)" if self.target_centric else " (Random)"
        return "Reactive Navigation" + suffix

    def get_description(self) -> str:
        """Get the algorithm description."""
        if self.target_centric:
            return "Uses sonar to avoid obstacles while moving toward target"
        return "Uses sonar to avoid obstacles with random direction selection"

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
        Compute direction using sonar sweep.

        Args:
            robot_x: Robot X position
            robot_y: Robot Y position
            robot_radius: Robot radius
            robot_heading: Current heading (not used in this algorithm)
            environment: Environment with obstacles and target
            sonar: Sonar sensor object

        Returns:
            Angle in degrees to move
        """
        if sonar is None:
            # Fallback: move toward target if no sonar
            angle_rad = math.atan2(
                environment.target.y - robot_y,
                environment.target.x - robot_x
            )
            return math.degrees(angle_rad)

        # Use sonar to find safe direction
        angle = sonar.sweep(
            robot_x, robot_y, environment,
            target_centric=self.target_centric,
            robot_radius=robot_radius
        )

        return angle

    def set_target_centric(self, enabled: bool) -> None:
        """
        Enable or disable target-centric mode.

        Args:
            enabled: If True, prefer directions toward target
        """
        self.target_centric = enabled

"""Sonar sensor for obstacle detection."""

import math
import random
from typing import List, Tuple
from src.config import SONAR_RANGE, SONAR_ANGLES
from src.environment import Environment


class Sonar:
    """Simulates a sonar sensor with multiple beams for obstacle detection."""

    def __init__(self, sonar_range: int = SONAR_RANGE) -> None:
        self.range = sonar_range
        self.angles = SONAR_ANGLES
        self.beams: List[Tuple[float, float, float, float]] = []  # (x1, y1, x2, y2) for each beam
        self.allowed_directions: List[int] = []

    def sweep(
        self,
        robot_x: float,
        robot_y: float,
        environment: Environment,
        target_centric: bool = False,
        robot_radius: float = 0,
    ) -> int:
        """
        Perform a sonar sweep and determine safe direction.

        Args:
            robot_x: Robot's x position
            robot_y: Robot's y position
            environment: Environment to check for obstacles
            target_centric: If True, prefer direction toward target

        Returns:
            Angle in degrees for safe movement direction
        """
        self.beams.clear()
        self.allowed_directions.clear()

        # Cast beams in all directions
        for angle in self.angles:
            rad = math.radians(angle)
            end_x = robot_x + self.range * math.cos(rad)
            end_y = robot_y + self.range * math.sin(rad)

            # Store beam for visualization
            self.beams.append((robot_x, robot_y, end_x, end_y))

            # Check if path is clear (accounting for robot radius)
            if environment.is_path_clear(robot_x, robot_y, end_x, end_y, robot_radius):
                self.allowed_directions.append(angle)

        # If target-centric mode is enabled, try to move toward target
        if target_centric and self.allowed_directions:
            # Calculate angle to target
            target_angle_rad = math.atan2(
                environment.target.y - robot_y,
                environment.target.x - robot_x
            )
            target_angle = math.degrees(target_angle_rad)
            # Normalize to 0-360
            if target_angle < 0:
                target_angle += 360

            # Find the closest safe direction to the target
            min_diff = float('inf')
            best_angle = None

            for angle in self.allowed_directions:
                # Calculate angular difference (accounting for wraparound)
                diff = abs(angle - target_angle)
                if diff > 180:
                    diff = 360 - diff

                if diff < min_diff:
                    min_diff = diff
                    best_angle = angle

            if best_angle is not None:
                chosen_angle = best_angle
            else:
                chosen_angle = random.choice(self.allowed_directions)
        elif self.allowed_directions:
            # No target-centric mode, choose randomly from safe directions
            chosen_angle = random.choice(self.allowed_directions)
        else:
            # If no safe directions, pick a random one anyway
            chosen_angle = random.choice(self.angles)

        # Return the angle directly - no conversion needed
        # The sonar already uses standard math angles (0°=East, 90°=North)
        # and robot.move() uses the same system
        return chosen_angle

    def calculate_target_heading(
        self, robot_x: float, robot_y: float, target_x: float, target_y: float
    ) -> float:
        """Calculate the heading from robot to target."""
        # Note: atan2 returns angle where 0 = East, positive = counterclockwise
        angle = math.atan2(target_y - robot_y, target_x - robot_x)
        return math.degrees(angle)

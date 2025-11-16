"""Potential field navigation algorithm."""

import math
from typing import Optional
from .base import NavigationAlgorithm
from src.environment import Environment


class PotentialFieldAlgorithm(NavigationAlgorithm):
    """
    Potential field navigation algorithm.

    This algorithm treats the target as an attractive force and obstacles as
    repulsive forces. The robot moves in the direction of the combined force vector.
    """

    def __init__(self, attractive_gain: float = 1.0, repulsive_gain: float = 50.0,
                 influence_distance: float = 100.0):
        """
        Initialize potential field algorithm.

        Args:
            attractive_gain: Strength of attraction to target
            repulsive_gain: Strength of repulsion from obstacles
            influence_distance: Max distance at which obstacles repel
        """
        super().__init__()
        self.attractive_gain = attractive_gain
        self.repulsive_gain = repulsive_gain
        self.influence_distance = influence_distance

    def get_name(self) -> str:
        """Get the algorithm name."""
        return "Potential Field"

    def get_description(self) -> str:
        """Get the algorithm description."""
        return "Uses attractive/repulsive forces to navigate"

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
        Compute direction using potential field method.

        Args:
            robot_x: Robot X position
            robot_y: Robot Y position
            robot_radius: Robot radius
            robot_heading: Current heading (not used)
            environment: Environment with obstacles and target
            sonar: Sonar sensor (not used in this algorithm)

        Returns:
            Angle in degrees toward combined force vector
        """
        # Attractive force toward target
        target_dx = environment.target.x - robot_x
        target_dy = environment.target.y - robot_y
        target_dist = math.sqrt(target_dx**2 + target_dy**2)

        if target_dist > 0:
            attractive_fx = self.attractive_gain * target_dx / target_dist
            attractive_fy = self.attractive_gain * target_dy / target_dist
        else:
            attractive_fx = 0
            attractive_fy = 0

        # Repulsive forces from obstacles
        repulsive_fx = 0.0
        repulsive_fy = 0.0

        for obstacle in environment.obstacles:
            # Calculate distance to obstacle
            if hasattr(obstacle, 'distance_to'):  # Circle
                obs_dist = obstacle.distance_to(robot_x, robot_y)
                obs_x = obstacle.x
                obs_y = obstacle.y
            else:  # Polygon - use centroid (simplified)
                points = obstacle.points
                obs_x = sum(p[0] for p in points) / len(points)
                obs_y = sum(p[1] for p in points) / len(points)
                obs_dist = math.sqrt((obs_x - robot_x)**2 + (obs_y - robot_y)**2)

            # Only repel if within influence distance
            if obs_dist < self.influence_distance and obs_dist > 0:
                # Repulsion strength increases as we get closer
                repulsion_strength = self.repulsive_gain * \
                    (1.0 / obs_dist - 1.0 / self.influence_distance) / (obs_dist**2)

                # Direction away from obstacle
                dx = robot_x - obs_x
                dy = robot_y - obs_y
                dist = math.sqrt(dx**2 + dy**2)

                if dist > 0:
                    repulsive_fx += repulsion_strength * dx / dist
                    repulsive_fy += repulsion_strength * dy / dist

        # Combine forces
        total_fx = attractive_fx + repulsive_fx
        total_fy = attractive_fy + repulsive_fy

        # Calculate angle from combined force
        angle_rad = math.atan2(total_fy, total_fx)
        angle_deg = math.degrees(angle_rad)

        # Normalize to 0-360
        if angle_deg < 0:
            angle_deg += 360

        # Snap to nearest 45-degree angle
        angle_deg = round(angle_deg / 45) * 45

        return angle_deg % 360

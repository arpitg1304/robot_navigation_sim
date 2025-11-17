"""Potential field navigation algorithm with tangential fields."""

import math
from typing import Optional
from .base import NavigationAlgorithm
from src.environment import Environment, Circle


class PotentialFieldAlgorithm(NavigationAlgorithm):
    """
    Potential field navigation algorithm with tangential fields.

    This algorithm treats the target as an attractive force and obstacles as
    repulsive forces. It also adds tangential forces to help navigate around
    obstacles and avoid local minima.
    """

    def __init__(self, attractive_gain: float = 1.5, repulsive_gain: float = 500.0,
                 influence_distance: float = 200.0):
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
        self.min_obstacle_distance = 20.0  # Safety margin
        self.stuck_counter = 0
        self.last_position = None

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
        Compute direction using potential field method with tangential fields.

        Args:
            robot_x: Robot X position
            robot_y: Robot Y position
            robot_radius: Robot radius
            robot_heading: Current heading
            environment: Environment with obstacles and target
            sonar: Sonar sensor (used as fallback)

        Returns:
            Angle in degrees toward combined force vector
        """
        # Check if robot is stuck (hasn't moved much)
        if self.last_position is not None:
            dist_moved = math.sqrt(
                (robot_x - self.last_position[0])**2 +
                (robot_y - self.last_position[1])**2
            )
            if dist_moved < 5:  # Very small movement
                self.stuck_counter += 1
            else:
                self.stuck_counter = max(0, self.stuck_counter - 1)

        self.last_position = (robot_x, robot_y)

        # If stuck for too long, use sonar-based navigation as fallback
        if self.stuck_counter > 10 and sonar is not None:
            self.stuck_counter = 0
            return sonar.sweep(robot_x, robot_y, environment,
                             target_centric=True, robot_radius=robot_radius)

        # Attractive force toward target
        target_dx = environment.target.x - robot_x
        target_dy = environment.target.y - robot_y
        target_dist = math.sqrt(target_dx**2 + target_dy**2)

        if target_dist > 0:
            # Normalize and scale by gain
            # Use quadratic attractive potential for smoother approach
            if target_dist > 50:
                attractive_fx = self.attractive_gain * target_dx / target_dist
                attractive_fy = self.attractive_gain * target_dy / target_dist
            else:
                # Reduce attraction near target to avoid overshooting
                attractive_fx = self.attractive_gain * target_dx / 50
                attractive_fy = self.attractive_gain * target_dy / 50
        else:
            attractive_fx = 0
            attractive_fy = 0

        # Repulsive forces from obstacles
        repulsive_fx = 0.0
        repulsive_fy = 0.0
        tangential_fx = 0.0
        tangential_fy = 0.0

        for obstacle in environment.obstacles:
            # Calculate distance to obstacle considering robot radius
            if isinstance(obstacle, Circle):
                # For circles, get distance from edge to edge
                center_dist = math.sqrt((obstacle.x - robot_x)**2 + (obstacle.y - robot_y)**2)
                obs_dist = center_dist - obstacle.radius - robot_radius
                obs_x = obstacle.x
                obs_y = obstacle.y
            else:  # Polygon
                # Use centroid for polygon (simplified approach)
                points = obstacle.points
                obs_x = sum(p[0] for p in points) / len(points)
                obs_y = sum(p[1] for p in points) / len(points)
                center_dist = math.sqrt((obs_x - robot_x)**2 + (obs_y - robot_y)**2)
                # Approximate distance (subtract estimated radius)
                obs_dist = center_dist - robot_radius - 40  # Approximate polygon size

            # Only repel if within influence distance
            if obs_dist < self.influence_distance:
                # Prevent division by zero and ensure minimum distance
                effective_dist = max(obs_dist, self.min_obstacle_distance)

                # Calculate repulsion strength (inversely proportional to distance squared)
                if effective_dist < self.influence_distance:
                    # Very strong repulsion when close
                    repulsion_strength = self.repulsive_gain / (effective_dist**2 + 1)

                    # Direction away from obstacle
                    dx = robot_x - obs_x
                    dy = robot_y - obs_y
                    dist = math.sqrt(dx**2 + dy**2)

                    if dist > 0.1:  # Avoid division by very small numbers
                        # Repulsive force (away from obstacle)
                        repulsive_fx += repulsion_strength * dx / dist
                        repulsive_fy += repulsion_strength * dy / dist

                        # Add tangential force to help navigate around obstacles
                        # This helps avoid local minima by adding sideways motion
                        if effective_dist < self.influence_distance * 0.7:
                            # Tangential direction (perpendicular to radial direction)
                            # Choose direction that aligns better with target
                            tang_x1 = -dy / dist  # One perpendicular direction
                            tang_y1 = dx / dist
                            tang_x2 = dy / dist   # Other perpendicular direction
                            tang_y2 = -dx / dist

                            # Pick tangent direction that's closer to target direction
                            dot1 = tang_x1 * target_dx + tang_y1 * target_dy
                            dot2 = tang_x2 * target_dx + tang_y2 * target_dy

                            if dot1 > dot2:
                                tang_strength = repulsion_strength * 0.3
                                tangential_fx += tang_strength * tang_x1
                                tangential_fy += tang_strength * tang_y1
                            else:
                                tang_strength = repulsion_strength * 0.3
                                tangential_fx += tang_strength * tang_x2
                                tangential_fy += tang_strength * tang_y2

        # Combine all forces
        total_fx = attractive_fx + repulsive_fx + tangential_fx
        total_fy = attractive_fy + repulsive_fy + tangential_fy

        # Normalize force magnitude to prevent excessive speeds
        force_magnitude = math.sqrt(total_fx**2 + total_fy**2)
        if force_magnitude > 5.0:
            total_fx = total_fx / force_magnitude * 5.0
            total_fy = total_fy / force_magnitude * 5.0

        # Calculate angle from combined force
        angle_rad = math.atan2(total_fy, total_fx)
        angle_deg = math.degrees(angle_rad)

        # Normalize to 0-360
        if angle_deg < 0:
            angle_deg += 360

        # Snap to nearest 45-degree angle for cleaner movement
        angle_deg = round(angle_deg / 45) * 45

        return angle_deg % 360

    def reset(self) -> None:
        """Reset algorithm state."""
        super().reset()
        self.stuck_counter = 0
        self.last_position = None

"""Template for creating custom navigation algorithms.

Copy this file and modify it to create your own algorithm!
"""

import math
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.base import NavigationAlgorithm
from src.environment import Environment


class TemplateAlgorithm(NavigationAlgorithm):
    """
    Template algorithm - replace this with your implementation.

    TODO: Describe what your algorithm does here.
    """

    def __init__(self):
        """Initialize your algorithm with any parameters needed."""
        super().__init__()
        # Add your initialization code here
        # Example:
        # self.some_parameter = 1.0
        # self.visited_positions = []

    def get_name(self) -> str:
        """Return the display name for your algorithm."""
        return "My Algorithm Name"

    def get_description(self) -> str:
        """Return a brief description of your algorithm."""
        return "Brief description of what this algorithm does"

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

        Args:
            robot_x: Current X position of the robot
            robot_y: Current Y position of the robot
            robot_radius: Radius of the robot (for collision checking)
            robot_heading: Current heading in degrees
            environment: Environment object with obstacles and target
            sonar: Sonar sensor object (None if disabled)

        Returns:
            Angle in degrees (0°=East, 90°=North, 180°=West, 270°=South)
        """
        # TODO: Implement your navigation algorithm here!

        # Example 1: Simple target seeking
        dx = environment.target.x - robot_x
        dy = environment.target.y - robot_y
        angle = math.degrees(math.atan2(dy, dx))

        # Normalize to 0-360
        if angle < 0:
            angle += 360

        # Snap to nearest 45-degree angle
        angle = round(angle / 45) * 45

        return angle % 360

        # Example 2: Using sonar for obstacle avoidance
        # if sonar is not None:
        #     # Get safe directions from sonar
        #     sonar.sweep(robot_x, robot_y, environment,
        #                target_centric=False, robot_radius=robot_radius)
        #
        #     if sonar.allowed_directions:
        #         # Pick the direction closest to target
        #         target_angle = math.degrees(math.atan2(
        #             environment.target.y - robot_y,
        #             environment.target.x - robot_x
        #         ))
        #         if target_angle < 0:
        #             target_angle += 360
        #
        #         best_angle = min(sonar.allowed_directions,
        #                        key=lambda a: abs(a - target_angle))
        #         return best_angle
        #
        # # Fallback: continue current heading
        # return robot_heading

    def reset(self) -> None:
        """
        Reset algorithm state when simulation restarts.

        Override this if your algorithm maintains internal state.
        """
        # Example:
        # self.visited_positions = []
        # self.stuck_count = 0
        pass

    def on_collision(self) -> None:
        """
        Called when the robot collides with an obstacle.

        Override this if you want to react to collisions.
        """
        # Example:
        # self.collision_count += 1
        # print(f"Collision detected! Total: {self.collision_count}")
        pass

    def on_target_reached(self) -> None:
        """
        Called when the robot reaches the target.

        Override this if you want to react to reaching the target.
        """
        # Example:
        # print(f"Target reached in {self.steps} steps!")
        pass


# To use this algorithm:
# 1. Copy this file to a new filename (e.g., my_algorithm.py)
# 2. Rename the class (e.g., MyCustomAlgorithm)
# 3. Implement the compute_direction() method
# 4. Add it to src/main.py:
#
#    from user_algorithms.my_algorithm import MyCustomAlgorithm
#
#    self.algorithms = [
#        # ... existing algorithms ...
#        MyCustomAlgorithm(),
#    ]

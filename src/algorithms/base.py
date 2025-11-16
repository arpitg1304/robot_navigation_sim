"""Base class for navigation algorithms."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from src.environment import Environment


class NavigationAlgorithm(ABC):
    """
    Base class for all navigation algorithms.

    To create your own navigation algorithm:
    1. Inherit from this class
    2. Implement the compute_direction() method
    3. Optionally override get_name() and get_description()
    4. Place your file in src/algorithms/ or user_algorithms/

    Example:
        class MyAlgorithm(NavigationAlgorithm):
            def get_name(self) -> str:
                return "My Custom Algorithm"

            def compute_direction(self, robot_x, robot_y, robot_radius,
                                environment, sonar) -> float:
                # Your algorithm logic here
                return 45.0  # Return angle in degrees
    """

    def __init__(self):
        """Initialize the navigation algorithm."""
        pass

    @abstractmethod
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
            robot_heading: Current heading of the robot in degrees
            environment: The environment containing obstacles and target
            sonar: Optional sonar sensor object (if your algorithm uses it)

        Returns:
            Angle in degrees where 0°=East, 90°=North, 180°=West, 270°=South

        Note:
            - environment.target has .x, .y, .radius attributes
            - environment.obstacles is a list of Circle or Polygon objects
            - environment.check_collision(x, y, margin) checks if position collides
            - environment.is_path_clear(x1, y1, x2, y2, margin) checks if path is clear
            - If sonar is provided, sonar.sweep() returns safe directions
        """
        pass

    def get_name(self) -> str:
        """
        Get the display name of this algorithm.

        Returns:
            Human-readable name for the algorithm
        """
        return self.__class__.__name__

    def get_description(self) -> str:
        """
        Get a brief description of this algorithm.

        Returns:
            Brief description of how the algorithm works
        """
        return "No description provided"

    def reset(self) -> None:
        """
        Reset the algorithm state (called when simulation restarts).

        Override this if your algorithm maintains internal state.
        """
        pass

    def on_collision(self) -> None:
        """
        Called when the robot collides with an obstacle.

        Override this if your algorithm needs to react to collisions.
        """
        pass

    def on_target_reached(self) -> None:
        """
        Called when the robot reaches the target.

        Override this if your algorithm needs to react to reaching the target.
        """
        pass

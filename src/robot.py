"""Robot class for the navigation simulator."""

import math
from typing import List, Tuple, Optional
from src.config import ROBOT_RADIUS, ROBOT_STEP_SIZE, ROBOT_START_X, ROBOT_START_Y
from src.sonar import Sonar
from src.environment import Environment
from src.algorithms.base import NavigationAlgorithm
from src.algorithms.reactive import ReactiveNavigationAlgorithm


class Robot:
    """Represents the navigating robot."""

    def __init__(self, algorithm: Optional[NavigationAlgorithm] = None) -> None:
        self.x = float(ROBOT_START_X)
        self.y = float(ROBOT_START_Y)
        self.radius = ROBOT_RADIUS
        self.step_size = ROBOT_STEP_SIZE
        self.heading = 0.0  # Current heading in degrees
        self.path_trace: List[Tuple[float, float]] = []
        self.sonar = Sonar()

        # Set navigation algorithm (default to reactive)
        self.algorithm = algorithm if algorithm is not None else ReactiveNavigationAlgorithm()

    def set_algorithm(self, algorithm: NavigationAlgorithm) -> None:
        """
        Set the navigation algorithm.

        Args:
            algorithm: Instance of a NavigationAlgorithm subclass
        """
        self.algorithm = algorithm
        self.algorithm.reset()

    def move(self, angle: float) -> None:
        """
        Move the robot in the specified direction.

        Args:
            angle: Direction to move in degrees
        """
        rad = math.radians(angle)
        self.x += self.step_size * math.cos(rad)
        self.y += self.step_size * math.sin(rad)
        self.heading = angle

    def manual_move(self, dx: float, dy: float) -> None:
        """Move the robot manually by delta x and y."""
        self.x += dx
        self.y += dy

    def check_target_reached(self, target_x: float, target_y: float, threshold: float) -> bool:
        """Check if robot has reached the target."""
        distance = math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)
        return distance <= threshold

    def navigate(
        self,
        environment: Environment,
        target_centric: bool = False,
        sonar_enabled: bool = True,
    ) -> None:
        """
        Navigate using the current navigation algorithm.

        Args:
            environment: The environment to navigate in
            target_centric: If True, prefer moving toward target (for compatible algorithms)
            sonar_enabled: If True, provide sonar to the algorithm

        Note:
            The target_centric parameter is maintained for backwards compatibility
            and is passed to ReactiveNavigationAlgorithm if it's the current algorithm.
        """
        # Update reactive algorithm if it's being used
        if isinstance(self.algorithm, ReactiveNavigationAlgorithm):
            self.algorithm.set_target_centric(target_centric)

        # Get direction from the algorithm
        sonar_obj = self.sonar if sonar_enabled else None
        angle = self.algorithm.compute_direction(
            self.x, self.y, self.radius, self.heading, environment, sonar_obj
        )

        # Check if the move would result in a collision
        rad = math.radians(angle)
        new_x = self.x + self.step_size * math.cos(rad)
        new_y = self.y + self.step_size * math.sin(rad)

        # Only move if the destination is safe
        if not environment.check_collision(new_x, new_y, self.radius):
            self.move(angle)
        else:
            # Notify algorithm of collision
            self.algorithm.on_collision()

    def record_position(self) -> None:
        """Record current position for path tracing."""
        self.path_trace.append((self.x, self.y))

    def save_path(self, filename: str) -> None:
        """Save path trace to file."""
        import numpy as np
        np.save(filename, self.path_trace)

    def load_path(self, filename: str) -> None:
        """Load path trace from file."""
        import numpy as np
        try:
            self.path_trace = list(np.load(filename, allow_pickle=True))
        except Exception as e:
            print(f"Warning: Could not load path from {filename}: {e}")

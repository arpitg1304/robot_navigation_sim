"""Gymnasium-compatible RL environment for the reactive navigation simulator."""

import math
from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from src.config import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    ROBOT_RADIUS,
    ROBOT_START_X,
    ROBOT_START_Y,
    SONAR_ANGLES,
    SONAR_RANGE,
    TARGET_DETECTION_DISTANCE,
)
from src.environment import Circle, Environment, Polygon
from src.sonar import Sonar


class ReactiveNavEnv(gym.Env):
    """
    Gymnasium environment for robot navigation with obstacles.

    Observation Space:
        - Sonar readings (8 values): normalized distances [0, 1]
        - Goal vector (2 values): normalized [dx, dy] to target [-1, 1]
        - Robot heading (2 values): [cos(θ), sin(θ)] in [-1, 1]
        - Linear velocity (1 value): normalized to [-1, 1]
        - Angular velocity (1 value): normalized to [-1, 1]
        Total: 14 dimensions

    Action Space (configurable):
        - Discrete (default): 3 actions [turn_left, go_straight, turn_right]
        - Continuous: [linear_vel, angular_vel] in [-1, 1]

    Reward Function:
        - +1.0 for reaching goal
        - -1.0 for collision
        - +distance_delta: reward for getting closer to goal
        - -0.01: small step penalty to encourage efficiency
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(
        self,
        map_name: str = "custom_map",
        max_steps: int = 500,
        action_type: str = "discrete",
        linear_vel_range: Tuple[float, float] = (0.0, 20.0),
        angular_vel_range: Tuple[float, float] = (-45.0, 45.0),
        render_mode: Optional[str] = None,
    ):
        """
        Initialize the navigation environment.

        Args:
            map_name: Name of the map to load from maps/ directory
            max_steps: Maximum steps per episode
            action_type: "discrete" or "continuous"
            linear_vel_range: (min, max) linear velocity in pixels/step
            angular_vel_range: (min, max) angular velocity in degrees/step
            render_mode: Rendering mode ("human" or "rgb_array")
        """
        super().__init__()

        self.map_name = map_name
        self.max_steps = max_steps
        self.action_type = action_type
        self.linear_vel_range = linear_vel_range
        self.angular_vel_range = angular_vel_range
        self.render_mode = render_mode

        # Environment state
        self.environment = Environment()
        self.sonar = Sonar()
        self.current_step = 0

        # Robot state (x, y, theta, linear_vel, angular_vel)
        self.robot_x = float(ROBOT_START_X)
        self.robot_y = float(ROBOT_START_Y)
        self.robot_theta = 0.0  # radians
        self.robot_linear_vel = 0.0
        self.robot_angular_vel = 0.0
        self.robot_radius = ROBOT_RADIUS

        # Track previous distance for reward shaping
        self.prev_distance_to_goal = 0.0

        # Define action space
        if action_type == "discrete":
            # 0: turn left, 1: go straight, 2: turn right
            self.action_space = spaces.Discrete(3)
        elif action_type == "continuous":
            # [linear_vel, angular_vel] normalized to [-1, 1]
            self.action_space = spaces.Box(
                low=np.array([-1.0, -1.0], dtype=np.float32),
                high=np.array([1.0, 1.0], dtype=np.float32),
                dtype=np.float32,
            )
        else:
            raise ValueError(f"Unknown action_type: {action_type}")

        # Define observation space
        # [8 sonar readings, 2 goal vector, 2 heading, 1 linear_vel, 1 angular_vel]
        self.observation_space = spaces.Box(
            low=np.array(
                [0.0] * 8  # sonar readings [0, 1]
                + [-1.0, -1.0]  # goal vector (normalized)
                + [-1.0, -1.0]  # heading (cos, sin)
                + [-1.0]  # linear velocity [-1, 1] (normalized from range)
                + [-1.0],  # angular velocity [-1, 1]
                dtype=np.float32,
            ),
            high=np.array(
                [1.0] * 8  # sonar
                + [1.0, 1.0]  # goal vector
                + [1.0, 1.0]  # heading
                + [1.0]  # linear velocity [-1, 1] (normalized from range)
                + [1.0],  # angular velocity
                dtype=np.float32,
            ),
            dtype=np.float32,
        )

        # Rendering
        self.renderer = None
        if render_mode == "human":
            self._init_renderer()

    def _init_renderer(self) -> None:
        """Initialize simple pygame renderer for RL visualization."""
        try:
            import pygame

            pygame.init()
            self.screen = pygame.display.set_mode((CANVAS_WIDTH, CANVAS_HEIGHT))
            pygame.display.set_caption("RL Agent Visualization")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 20)
            self.renderer = True  # Flag that rendering is enabled
        except ImportError:
            print("Warning: pygame not available, rendering disabled")
            self.renderer = None

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.

        Returns:
            observation: Initial observation
            info: Additional information dictionary
        """
        super().reset(seed=seed)

        # Load map
        self.environment.load_map(self.map_name)

        # Reset robot to start position
        self.robot_x, self.robot_y = self.environment.robot_start
        self.robot_theta = 0.0
        self.robot_linear_vel = 0.0
        self.robot_angular_vel = 0.0

        # Reset step counter
        self.current_step = 0

        # Calculate initial distance to goal
        self.prev_distance_to_goal = self._distance_to_goal()

        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def step(
        self, action: np.ndarray
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.

        Args:
            action: Action to execute

        Returns:
            observation: New observation after action
            reward: Reward for this step
            terminated: Whether episode ended (goal reached or collision)
            truncated: Whether episode was truncated (max steps)
            info: Additional information
        """
        self.current_step += 1

        # Parse action and update velocities
        if self.action_type == "discrete":
            # 0: turn left, 1: go straight, 2: turn right
            if action == 0:
                self.robot_angular_vel = self.angular_vel_range[1]  # Turn left (positive)
                self.robot_linear_vel = self.linear_vel_range[1] * 0.5  # Half speed when turning
            elif action == 1:
                self.robot_angular_vel = 0.0  # Go straight
                self.robot_linear_vel = self.linear_vel_range[1]  # Full speed
            elif action == 2:
                self.robot_angular_vel = self.angular_vel_range[0]  # Turn right (negative)
                self.robot_linear_vel = self.linear_vel_range[1] * 0.5  # Half speed when turning
        else:
            # Continuous action: denormalize from [-1, 1]
            linear_action, angular_action = action
            self.robot_linear_vel = self._denormalize(
                linear_action, self.linear_vel_range[0], self.linear_vel_range[1]
            )
            self.robot_angular_vel = self._denormalize(
                angular_action, self.angular_vel_range[0], self.angular_vel_range[1]
            )

        # Update robot heading (theta)
        self.robot_theta += math.radians(self.robot_angular_vel)
        self.robot_theta = self._normalize_angle(self.robot_theta)

        # Calculate new position
        new_x = self.robot_x + self.robot_linear_vel * math.cos(self.robot_theta)
        new_y = self.robot_y + self.robot_linear_vel * math.sin(self.robot_theta)

        # Check for collision
        collision = self.environment.check_collision(new_x, new_y, self.robot_radius)

        # Calculate reward
        reward = 0.0
        terminated = False

        if collision:
            # Collision penalty
            reward = -1.0
            terminated = True
        else:
            # Update position (only if no collision)
            self.robot_x = new_x
            self.robot_y = new_y

            # Check if goal reached
            current_distance = self._distance_to_goal()
            goal_reached = current_distance <= TARGET_DETECTION_DISTANCE

            if goal_reached:
                # Goal reward
                reward = 1.0
                terminated = True
            else:
                # Distance-based reward shaping
                distance_delta = self.prev_distance_to_goal - current_distance
                reward = distance_delta / 100.0  # Normalize by typical distances

                # Small step penalty for efficiency
                reward -= 0.01

                # Update previous distance
                self.prev_distance_to_goal = current_distance

        # Check truncation (max steps)
        truncated = self.current_step >= self.max_steps

        # Get observation and info
        observation = self._get_observation()
        info = self._get_info()
        info["collision"] = collision
        info["goal_reached"] = terminated and not collision

        return observation, reward, terminated, truncated, info

    def render(self) -> Optional[np.ndarray]:
        """Render the environment."""
        if self.render_mode is None:
            return None

        if self.renderer is None:
            self._init_renderer()

        if self.renderer is not None:
            import pygame

            # Clear screen
            self.screen.fill((245, 245, 247))  # Light gray background

            # Draw obstacles
            for obstacle in self.environment.obstacles:
                if isinstance(obstacle, Circle):
                    pygame.draw.circle(
                        self.screen,
                        (71, 85, 105),  # Dark gray
                        (int(obstacle.x), int(obstacle.y)),
                        int(obstacle.radius),
                    )
                    pygame.draw.circle(
                        self.screen,
                        (51, 65, 85),
                        (int(obstacle.x), int(obstacle.y)),
                        int(obstacle.radius),
                        2,
                    )
                elif isinstance(obstacle, Polygon):
                    points = [(int(p[0]), int(p[1])) for p in obstacle.points]
                    pygame.draw.polygon(self.screen, (71, 85, 105), points)
                    pygame.draw.polygon(self.screen, (51, 65, 85), points, 2)

            # Draw walls
            for wall in self.environment.walls:
                points = [(int(p[0]), int(p[1])) for p in wall.points]
                pygame.draw.polygon(self.screen, (100, 100, 100), points)

            # Draw target
            target = self.environment.target
            pygame.draw.circle(
                self.screen,
                (251, 191, 36),  # Amber
                (int(target.x), int(target.y)),
                int(target.radius),
            )
            pygame.draw.circle(
                self.screen,
                (253, 224, 71),  # Yellow outline
                (int(target.x), int(target.y)),
                int(target.radius),
                3,
            )

            # Draw robot
            pygame.draw.circle(
                self.screen,
                (59, 130, 246),  # Blue
                (int(self.robot_x), int(self.robot_y)),
                self.robot_radius,
            )

            # Draw heading indicator
            heading_length = 15
            end_x = self.robot_x + heading_length * math.cos(self.robot_theta)
            end_y = self.robot_y + heading_length * math.sin(self.robot_theta)
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (int(self.robot_x), int(self.robot_y)),
                (int(end_x), int(end_y)),
                3,
            )

            # Draw info text
            info_texts = [
                f"Step: {self.current_step}",
                f"Distance: {self._distance_to_goal():.1f}",
                f"Position: ({self.robot_x:.0f}, {self.robot_y:.0f})",
            ]

            y_offset = 10
            for text in info_texts:
                text_surface = self.font.render(text, True, (0, 0, 0))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 25

            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

            if self.render_mode == "rgb_array":
                # Return RGB array
                return np.transpose(
                    np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
                )

        return None

    def close(self) -> None:
        """Clean up resources."""
        if self.renderer is not None:
            import pygame
            pygame.quit()
            self.renderer = None

    def _get_observation(self) -> np.ndarray:
        """
        Construct observation vector.

        Returns:
            14-dimensional observation:
            - 8 sonar readings (normalized to [0, 1])
            - 2 goal vector components (normalized to [-1, 1])
            - 2 heading components (cos, sin in [-1, 1])
            - 1 linear velocity (normalized to [-1, 1])
            - 1 angular velocity (normalized to [-1, 1])
        """
        # Sonar readings
        sonar_readings = self._get_sonar_readings()

        # Goal vector (normalized)
        dx = self.environment.target.x - self.robot_x
        dy = self.environment.target.y - self.robot_y
        distance = math.sqrt(dx**2 + dy**2)
        goal_vector = [
            dx / max(distance, 1.0),  # Normalize by distance (avoid div by zero)
            dy / max(distance, 1.0),
        ]

        # Heading (cos, sin representation)
        heading = [math.cos(self.robot_theta), math.sin(self.robot_theta)]

        # Velocities (normalized)
        linear_vel_norm = self._normalize(
            self.robot_linear_vel, self.linear_vel_range[0], self.linear_vel_range[1]
        )
        angular_vel_norm = self._normalize(
            self.robot_angular_vel, self.angular_vel_range[0], self.angular_vel_range[1]
        )

        observation = np.array(
            sonar_readings + goal_vector + heading + [linear_vel_norm, angular_vel_norm],
            dtype=np.float32,
        )

        return observation

    def _get_sonar_readings(self) -> list:
        """
        Get normalized sonar readings in 8 directions.

        Returns:
            List of 8 normalized distances [0, 1]
        """
        readings = []

        for angle_deg in SONAR_ANGLES:
            # Convert to absolute angle (robot's frame + sonar angle)
            absolute_angle = self.robot_theta + math.radians(angle_deg)

            # Cast ray to find obstacle distance
            distance = self._cast_ray(self.robot_x, self.robot_y, absolute_angle)

            # Normalize to [0, 1] where 1 = max range (clear), 0 = obstacle right there
            normalized_distance = min(distance / SONAR_RANGE, 1.0)
            readings.append(normalized_distance)

        return readings

    def _cast_ray(self, x: float, y: float, angle: float) -> float:
        """
        Cast a ray from (x, y) at given angle and return distance to nearest obstacle.

        Args:
            x, y: Starting position
            angle: Ray angle in radians

        Returns:
            Distance to nearest obstacle (or SONAR_RANGE if no obstacle)
        """
        # Sample along the ray
        step_size = 5.0
        max_distance = SONAR_RANGE

        for distance in np.arange(0, max_distance, step_size):
            test_x = x + distance * math.cos(angle)
            test_y = y + distance * math.sin(angle)

            if self.environment.check_collision(test_x, test_y, 0):
                return distance

        return max_distance

    def _distance_to_goal(self) -> float:
        """Calculate Euclidean distance to goal."""
        dx = self.environment.target.x - self.robot_x
        dy = self.environment.target.y - self.robot_y
        return math.sqrt(dx**2 + dy**2)

    def _get_info(self) -> Dict[str, Any]:
        """Get additional information dictionary."""
        return {
            "robot_x": self.robot_x,
            "robot_y": self.robot_y,
            "robot_theta": self.robot_theta,
            "distance_to_goal": self._distance_to_goal(),
            "step": self.current_step,
        }

    @staticmethod
    def _normalize(value: float, min_val: float, max_val: float) -> float:
        """Normalize value from [min_val, max_val] to [-1, 1]."""
        return 2.0 * (value - min_val) / (max_val - min_val) - 1.0

    @staticmethod
    def _denormalize(value: float, min_val: float, max_val: float) -> float:
        """Denormalize value from [-1, 1] to [min_val, max_val]."""
        return (value + 1.0) * (max_val - min_val) / 2.0 + min_val

    @staticmethod
    def _normalize_angle(angle: float) -> float:
        """Normalize angle to [-π, π]."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

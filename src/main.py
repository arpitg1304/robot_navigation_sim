"""Main entry point for the reactive navigation simulator."""

import pygame
import sys
from pathlib import Path
from src.robot import Robot
from src.environment import Environment
from src.modern_renderer import ModernRenderer
from src.config import (
    FPS,
    MOVE_INTERVAL,
    TARGET_DETECTION_DISTANCE,
    SimulationState,
)
from src.algorithms import (
    ReactiveNavigationAlgorithm,
    SimpleTargetSeekingAlgorithm,
    WallFollowerAlgorithm,
    PotentialFieldAlgorithm,
)


class Simulator:
    """Main simulator class."""

    def __init__(self) -> None:
        self.robot = Robot()
        self.environment = Environment()
        self.renderer = ModernRenderer()
        self.state = SimulationState()
        self.clock = pygame.time.Clock()
        self.frame_count = 0

        # Available algorithms
        self.algorithms = [
            ReactiveNavigationAlgorithm(target_centric=False),
            ReactiveNavigationAlgorithm(target_centric=True),
            SimpleTargetSeekingAlgorithm(),
            WallFollowerAlgorithm(),
            PotentialFieldAlgorithm(),
        ]
        self.current_algorithm_index = 1  # Start with reactive target-centric
        self.robot.set_algorithm(self.algorithms[self.current_algorithm_index])

        # Get available maps
        self.available_maps = Environment.get_available_maps()
        self.current_map_index = 0
        self.current_map_name = None

        # Initialize algorithm dropdown
        algorithm_names = [algo.get_name() for algo in self.algorithms]
        self.renderer.create_algorithm_dropdown(
            algorithm_names,
            self.current_algorithm_index,
            self._on_algorithm_selected
        )

        # Initialize map dropdown if maps are available
        if self.available_maps:
            self.renderer.create_map_dropdown(
                self.available_maps,
                self.current_map_index,
                self._on_map_selected
            )

        # Try to load default map
        self._load_default_map()

    def _on_algorithm_selected(self, index: int) -> None:
        """Callback when algorithm is selected from dropdown."""
        self.current_algorithm_index = index
        self.robot.set_algorithm(self.algorithms[index])
        algo_name = self.robot.algorithm.get_name()
        print(f"Algorithm changed to: {algo_name}")

    def _on_map_selected(self, index: int) -> None:
        """Callback when map is selected from dropdown."""
        self.current_map_index = index
        map_name = self.available_maps[index]

        # Load the selected map
        if self.environment.load_map(map_name):
            self.current_map_name = map_name
            print(f"Map changed to: {map_name}")
            # Reset simulation when map changes
            self._reset_simulation()
        else:
            print(f"Failed to load map: {map_name}")

    def _load_default_map(self) -> None:
        """Load the default map if it exists."""
        # Try to load first available map from maps directory
        if self.available_maps:
            map_name = self.available_maps[0]
            if self.environment.load_map(map_name):
                self.current_map_name = map_name
                self.current_map_index = 0
                print(f"Loaded map: {map_name}")
                return

        # Fallback: try legacy .npy files in parent directory
        legacy_path = Path(__file__).parent.parent.parent / "reactive_navigation_simulator"
        target_file = legacy_path / "only_target.npy"
        obstacles_file = legacy_path / "polygons2.npy"

        if target_file.exists() and obstacles_file.exists():
            self.environment.load_from_numpy(str(target_file), str(obstacles_file))
            print("Loaded legacy map from reactive_navigation_simulator/")
            return

        print("No maps found. Create a map using: python -m tools.map_editor")

    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if quit requested."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle button clicks
            button_name = self.renderer.handle_button_events(event)
            if button_name:
                self._handle_button_click(button_name)
                if button_name == "quit":
                    return False

            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                self._handle_keypress(event.key)

        return True

    def _handle_button_click(self, button_name: str) -> None:
        """Handle button click events."""
        if button_name == "start_stop":
            self.state.running = not self.state.running
            print(f"Simulation {'started' if self.state.running else 'stopped'}")

        elif button_name == "algorithm_changed":
            # Already handled by dropdown callback
            pass

        elif button_name == "sonar":
            self.state.sonar_enabled = not self.state.sonar_enabled
            print(f"Sonar {'enabled' if self.state.sonar_enabled else 'disabled'}")

        elif button_name == "tracking":
            self.state.tracking_enabled = not self.state.tracking_enabled
            print(f"Path tracking {'enabled' if self.state.tracking_enabled else 'disabled'}")

        elif button_name == "save":
            self.robot.save_path("robot_trace.npy")
            print("Path saved to robot_trace.npy")

        elif button_name == "reset":
            self._reset_simulation()

    def _handle_keypress(self, key: int) -> None:
        """Handle keyboard input for manual control."""
        step = 10
        if key == pygame.K_UP:
            self.robot.manual_move(0, -step)
        elif key == pygame.K_DOWN:
            self.robot.manual_move(0, step)
        elif key == pygame.K_LEFT:
            self.robot.manual_move(-step, 0)
        elif key == pygame.K_RIGHT:
            self.robot.manual_move(step, 0)
        elif key == pygame.K_SPACE:
            self.state.running = not self.state.running
        elif key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _reset_simulation(self) -> None:
        """Reset the simulation."""
        from src.config import ROBOT_START_X, ROBOT_START_Y
        self.robot.x = float(ROBOT_START_X)
        self.robot.y = float(ROBOT_START_Y)
        self.robot.heading = 0.0
        self.robot.path_trace = []
        self.state.running = False
        self.state.target_reached = False
        self.robot.algorithm.reset()
        print("Simulation reset")

    def update(self) -> None:
        """Update the simulation state."""
        self.frame_count += 1

        # Check if target is reached
        if self.robot.check_target_reached(
            self.environment.target.x,
            self.environment.target.y,
            TARGET_DETECTION_DISTANCE,
        ):
            if not self.state.target_reached:
                print("Target reached!")
                self.state.target_reached = True
                self.state.running = False

        # Move robot if simulation is running
        if self.state.running and not self.state.target_reached:
            if self.frame_count % MOVE_INTERVAL == 0:
                self.robot.navigate(
                    self.environment,
                    target_centric=self.state.target_centric,
                    sonar_enabled=self.state.sonar_enabled,
                )
                if self.state.tracking_enabled:
                    self.robot.record_position()

    def render(self) -> None:
        """Render the simulation."""
        # Draw environment
        sonar_beams = self.robot.sonar.beams if self.state.sonar_enabled else None
        self.renderer.draw_environment(
            self.environment,
            show_sonar=self.state.sonar_enabled and self.state.running,
            sonar_beams=sonar_beams,
        )

        # Draw path trace if enabled
        if self.state.tracking_enabled:
            self.renderer.draw_path_trace(self.robot)

        # Draw robot
        self.renderer.draw_robot(self.robot)

        # Draw UI
        algo_name = self.robot.algorithm.get_name()
        self.renderer.draw_ui_panel(self.robot, self.state, algo_name)

        # Draw bottom control bar
        self.renderer.update_button_states(self.state)
        self.renderer.draw_bottom_bar()

        # Draw dropdown on top of everything (so it's not covered)
        self.renderer.draw_dropdown_on_top()

        # Update display
        self.renderer.update()

    def run(self) -> None:
        """Main simulation loop."""
        print("=" * 60)
        print("Reactive Navigation Simulator - Modern UI")
        print("=" * 60)
        print("\nControls:")
        print("  - Click 'Start/Stop' or press SPACE to start/stop simulation")
        print("  - Use dropdown to select navigation algorithm")
        print("  - Arrow keys for manual control")
        print("  - Toggle buttons to control features")
        print("  - ESC to quit")
        print(f"\nCurrent algorithm: {self.robot.algorithm.get_name()}")
        print(f"Available algorithms: {len(self.algorithms)}")
        print("=" * 60)
        print()

        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main() -> None:
    """Entry point for the application."""
    simulator = Simulator()
    simulator.run()


if __name__ == "__main__":
    main()

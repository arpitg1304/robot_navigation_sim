"""Modern Pygame-based renderer for the navigation simulator."""

import pygame
import math
from typing import Optional, List
from src.robot import Robot
from src.environment import Environment, Circle, Polygon
from src.config import *
from src.ui_components import ModernButton, Dropdown, ToggleSwitch, StatCard


class ModernRenderer:
    """Handles all rendering with a modern, polished UI."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Reactive Navigation Simulator - Modern UI")

        # Fonts
        self.font_title = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 28)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)

        # UI Components
        self._create_ui_components()

        # Animation state
        self.target_pulse = 0
        self.frame_count = 0

    def _create_ui_components(self) -> None:
        """Create all UI components."""
        # Control buttons (bottom bar)
        button_y = WINDOW_HEIGHT - 60
        button_height = 45
        button_width = 110

        self.buttons = {
            "start_stop": ModernButton(
                10, button_y, button_width, button_height, "Start/Stop"
            ),
            "sonar": ModernButton(
                130, button_y, button_width, button_height, "Sonar"
            ),
            "tracking": ModernButton(
                250, button_y, button_width, button_height, "Tracking"
            ),
            "save": ModernButton(
                370, button_y, 90, button_height, "Save"
            ),
            "reset": ModernButton(
                470, button_y, 90, button_height, "Reset"
            ),
            "quit": ModernButton(
                570, button_y, 80, button_height, "Quit"
            ),
        }

        # Dropdowns (will be initialized with actual data)
        self.algorithm_dropdown = None
        self.map_dropdown = None

    def create_algorithm_dropdown(
        self, algorithms: List[str], selected: int, on_select
    ) -> None:
        """Create the algorithm dropdown with actual algorithm list."""
        self.algorithm_dropdown = Dropdown(
            x=CANVAS_WIDTH + 20,
            y=85,  # Below "Algorithm:" label
            width=WINDOW_WIDTH - CANVAS_WIDTH - 40,
            height=35,
            options=algorithms,
            selected_index=selected,
            on_select=on_select,
        )

    def create_map_dropdown(
        self, maps: List[str], selected: int, on_select
    ) -> None:
        """Create the map dropdown with actual map list."""
        # Place map dropdown below algorithm dropdown
        y_offset = 155  # Below "Map:" label (85 + 35 + 15 spacing + 20 label)
        self.map_dropdown = Dropdown(
            x=CANVAS_WIDTH + 20,
            y=y_offset,
            width=WINDOW_WIDTH - CANVAS_WIDTH - 40,
            height=35,
            options=maps,
            selected_index=selected,
            on_select=on_select,
        )

    def draw_environment(
        self, environment: Environment, show_sonar: bool = False, sonar_beams=None
    ) -> None:
        """Draw the environment with modern styling."""
        # Draw canvas background with subtle gradient
        canvas_rect = pygame.Rect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_CANVAS_BG, canvas_rect)

        # Draw grid pattern for depth
        self._draw_grid()

        # Draw obstacles with shadows and modern styling
        for obstacle in environment.obstacles:
            if isinstance(obstacle, Circle):
                # Shadow
                shadow_offset = 3
                pygame.draw.circle(
                    self.screen,
                    (0, 0, 0, 30),
                    (int(obstacle.x + shadow_offset), int(obstacle.y + shadow_offset)),
                    int(obstacle.radius),
                )
                # Obstacle
                pygame.draw.circle(
                    self.screen,
                    COLOR_OBSTACLE,
                    (int(obstacle.x), int(obstacle.y)),
                    int(obstacle.radius),
                )
                # Outline
                pygame.draw.circle(
                    self.screen,
                    COLOR_OBSTACLE_OUTLINE,
                    (int(obstacle.x), int(obstacle.y)),
                    int(obstacle.radius),
                    3,
                )
            elif isinstance(obstacle, Polygon):
                # Shadow
                shadow_points = [(p[0] + 3, p[1] + 3) for p in obstacle.points]
                pygame.draw.polygon(self.screen, (0, 0, 0, 30), shadow_points)
                # Obstacle
                pygame.draw.polygon(self.screen, COLOR_OBSTACLE, obstacle.points)
                # Outline
                pygame.draw.polygon(
                    self.screen, COLOR_OBSTACLE_OUTLINE, obstacle.points, 3
                )

        # Draw walls (boundaries)
        for wall in environment.walls:
            pygame.draw.polygon(self.screen, COLOR_BG_LIGHT, wall.points)

        # Draw target with glow effect
        self._draw_target(environment.target)

        # Draw sonar beams
        if show_sonar and sonar_beams:
            self._draw_sonar_beams(sonar_beams, environment)

    def _draw_grid(self) -> None:
        """Draw subtle grid pattern."""
        grid_color = (220, 220, 225)
        grid_spacing = 50

        for x in range(0, CANVAS_WIDTH, grid_spacing):
            pygame.draw.line(
                self.screen, grid_color, (x, 0), (x, CANVAS_HEIGHT), 1
            )

        for y in range(0, CANVAS_HEIGHT, grid_spacing):
            pygame.draw.line(
                self.screen, grid_color, (0, y), (CANVAS_WIDTH, y), 1
            )

    def _draw_target(self, target: Circle) -> None:
        """Draw target with pulsing glow effect."""
        # Animate pulse
        self.target_pulse = (self.target_pulse + 0.05) % (2 * math.pi)
        pulse_factor = 0.8 + 0.2 * math.sin(self.target_pulse)

        # Outer glow (multiple layers)
        for i in range(4, 0, -1):
            glow_radius = int(target.radius * (1 + i * 0.3 * pulse_factor))
            glow_alpha = int(30 / i)
            glow_surf = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surf,
                (*COLOR_TARGET_GLOW, glow_alpha),
                (glow_radius, glow_radius),
                glow_radius,
            )
            self.screen.blit(
                glow_surf,
                (
                    int(target.x - glow_radius),
                    int(target.y - glow_radius),
                ),
            )

        # Main target
        pygame.draw.circle(
            self.screen,
            COLOR_TARGET,
            (int(target.x), int(target.y)),
            int(target.radius),
        )

        # Inner circle
        inner_radius = int(target.radius * 0.6)
        pygame.draw.circle(
            self.screen,
            COLOR_TARGET_GLOW,
            (int(target.x), int(target.y)),
            inner_radius,
        )

        # Center dot
        pygame.draw.circle(
            self.screen, COLOR_WHITE, (int(target.x), int(target.y)), 4
        )

    def _draw_sonar_beams(self, beams, environment) -> None:
        """Draw sonar beams with modern styling."""
        for i, beam in enumerate(beams):
            x1, y1, x2, y2 = beam

            # Check if path is clear
            is_clear = environment.is_path_clear(x1, y1, x2, y2, 10)
            color = COLOR_SONAR_LINE if is_clear else COLOR_SONAR_BLOCKED

            # Draw beam with alpha
            pygame.draw.aaline(self.screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 2)

            # Draw endpoint indicator
            pygame.draw.circle(self.screen, color, (int(x2), int(y2)), 4)

    def draw_robot(self, robot: Robot) -> None:
        """Draw robot with modern styling and direction indicator."""
        robot_x, robot_y = int(robot.x), int(robot.y)
        radius = robot.radius

        # Shadow
        shadow_offset = 2
        shadow_surf = pygame.Surface((radius * 2 + 10, radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(
            shadow_surf,
            (0, 0, 0, 60),
            (radius + 5 + shadow_offset, radius + 5 + shadow_offset),
            radius,
        )
        self.screen.blit(
            shadow_surf, (robot_x - radius - 5, robot_y - radius - 5)
        )

        # Robot body
        pygame.draw.circle(self.screen, COLOR_ROBOT, (robot_x, robot_y), radius)

        # Robot outline
        pygame.draw.circle(
            self.screen, COLOR_ACCENT_SECONDARY, (robot_x, robot_y), radius, 3
        )

        # Direction indicator
        angle_rad = math.radians(robot.heading)
        indicator_length = radius * 1.5
        end_x = robot_x + indicator_length * math.cos(angle_rad)
        end_y = robot_y + indicator_length * math.sin(angle_rad)

        pygame.draw.line(
            self.screen,
            COLOR_WHITE,
            (robot_x, robot_y),
            (int(end_x), int(end_y)),
            3,
        )

        # Center dot
        pygame.draw.circle(self.screen, COLOR_WHITE, (robot_x, robot_y), 3)

    def draw_path_trace(self, robot: Robot) -> None:
        """Draw the robot's path trace with gradient effect."""
        if len(robot.path_trace) < 2:
            return

        # Draw path with fading effect
        path_points = robot.path_trace[-100:]  # Last 100 points

        for i in range(len(path_points) - 1):
            # Calculate alpha based on position in path (newer = more visible)
            alpha = int(100 + (i / len(path_points)) * 155)
            thickness = 2 + int((i / len(path_points)) * 2)

            p1 = (int(path_points[i][0]), int(path_points[i][1]))
            p2 = (int(path_points[i + 1][0]), int(path_points[i + 1][1]))

            # Draw segment
            color = (*COLOR_PATH_TRACE, alpha)
            surf = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(surf, color, p1, p2, thickness)
            self.screen.blit(surf, (0, 0))

    def draw_ui_panel(self, robot: Robot, state, algorithm_name: str) -> None:
        """Draw modern UI panel."""
        panel_x = CANVAS_WIDTH
        panel_width = WINDOW_WIDTH - CANVAS_WIDTH
        panel_height = CANVAS_HEIGHT

        # Draw panel background
        pygame.draw.rect(
            self.screen,
            COLOR_UI_BG,
            (panel_x, 0, panel_width, panel_height),
        )

        # Draw title
        title_surface = self.font_title.render("Navigation", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(title_surface, (panel_x + 20, 20))

        # Algorithm dropdown label (draw dropdown itself later, on top)
        algo_label = self.font_small.render("Algorithm:", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(algo_label, (panel_x + 20, 65))

        # Map dropdown label (draw dropdown itself later, on top)
        if self.map_dropdown:
            map_label = self.font_small.render("Map:", True, COLOR_TEXT_SECONDARY)
            self.screen.blit(map_label, (panel_x + 20, 135))

        # Stats section
        stats_y = 200 if self.map_dropdown else 130  # Adjusted to fit below both dropdowns or just algorithm
        stat_height = 70
        stat_spacing = 15

        # Position stat
        StatCard(
            panel_x + 20,
            stats_y,
            panel_width - 40,
            stat_height,
            "Position",
            f"({robot.x:.0f}, {robot.y:.0f})",
        ).draw(self.screen, self.font_small, self.font_medium)

        # Heading stat
        StatCard(
            panel_x + 20,
            stats_y + stat_height + stat_spacing,
            panel_width - 40,
            stat_height,
            "Heading",
            f"{robot.heading:.1f}°",
        ).draw(self.screen, self.font_small, self.font_medium)

        # Status indicators
        status_y = stats_y + 2 * (stat_height + stat_spacing) + 30

        # Draw status section header
        status_header = self.font_medium.render("Status", True, COLOR_TEXT_PRIMARY)
        self.screen.blit(status_header, (panel_x + 20, status_y - 30))

        # Status items
        status_items = [
            ("Running", state.running, COLOR_SUCCESS),
            ("Sonar", state.sonar_enabled, COLOR_ACCENT_PRIMARY),
            ("Tracking", state.tracking_enabled, COLOR_ACCENT_SECONDARY),
        ]

        for i, (label, active, color) in enumerate(status_items):
            y_pos = status_y + i * 35

            # Status indicator dot
            indicator_color = color if active else COLOR_BG_LIGHT
            pygame.draw.circle(
                self.screen, indicator_color, (panel_x + 30, y_pos + 10), 6
            )

            # Label
            text_color = COLOR_TEXT_PRIMARY if active else COLOR_TEXT_SECONDARY
            text = self.font_small.render(label, True, text_color)
            self.screen.blit(text, (panel_x + 50, y_pos + 2))

        # Target reached message
        if state.target_reached:
            msg_y = status_y + len(status_items) * 35 + 30
            success_bg = pygame.Rect(panel_x + 20, msg_y, panel_width - 40, 50)
            pygame.draw.rect(self.screen, COLOR_SUCCESS, success_bg, border_radius=8)

            msg_text = self.font_medium.render("TARGET REACHED!", True, COLOR_WHITE)
            msg_rect = msg_text.get_rect(center=success_bg.center)
            self.screen.blit(msg_text, msg_rect)

    def draw_dropdown_on_top(self) -> None:
        """Draw dropdowns on top of everything else."""
        # Draw closed dropdowns first
        if self.algorithm_dropdown and not self.algorithm_dropdown.is_open:
            self.algorithm_dropdown.draw(self.screen, self.font_small)
        if self.map_dropdown and not self.map_dropdown.is_open:
            self.map_dropdown.draw(self.screen, self.font_small)

        # Draw open dropdown last (on top of everything)
        if self.algorithm_dropdown and self.algorithm_dropdown.is_open:
            self.algorithm_dropdown.draw(self.screen, self.font_small)
        if self.map_dropdown and self.map_dropdown.is_open:
            self.map_dropdown.draw(self.screen, self.font_small)

    def draw_bottom_bar(self) -> None:
        """Draw bottom control bar."""
        # Background
        bar_rect = pygame.Rect(0, WINDOW_HEIGHT - 80, WINDOW_WIDTH, 80)
        pygame.draw.rect(self.screen, COLOR_UI_PANEL, bar_rect)

        # Top border
        pygame.draw.line(
            self.screen,
            COLOR_BG_LIGHT,
            (0, WINDOW_HEIGHT - 80),
            (WINDOW_WIDTH, WINDOW_HEIGHT - 80),
            2,
        )

        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen, self.font_small)

    def handle_button_events(self, event: pygame.event.Event) -> Optional[str]:
        """Handle button click events. Returns button name if clicked."""
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name

        # Handle algorithm dropdown
        if self.algorithm_dropdown and self.algorithm_dropdown.handle_event(event):
            return "algorithm_changed"

        # Handle map dropdown
        if self.map_dropdown and self.map_dropdown.handle_event(event):
            return "map_changed"

        return None

    def update_button_states(self, state) -> None:
        """Update button active states based on simulation state."""
        self.buttons["start_stop"].is_active = state.running
        self.buttons["sonar"].is_active = state.sonar_enabled
        self.buttons["tracking"].is_active = state.tracking_enabled

    def update(self) -> None:
        """Update the display."""
        self.frame_count += 1
        pygame.display.flip()

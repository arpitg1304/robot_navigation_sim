"""Pygame-based renderer for the navigation simulator."""

import pygame
from typing import Optional
from src.robot import Robot
from src.environment import Environment, Circle, Polygon
from src.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    CANVAS_WIDTH,
    CANVAS_HEIGHT,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_ROBOT,
    COLOR_TARGET,
    COLOR_OBSTACLE,
    COLOR_OBSTACLE_OUTLINE,
    COLOR_PATH_TRACE,
    COLOR_SONAR_LINE,
    COLOR_UI_BG,
    COLOR_UI_TEXT,
    COLOR_BUTTON,
    COLOR_BUTTON_ACTIVE,
    SimulationState,
)


class Button:
    """Simple button for the UI."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button."""
        color = COLOR_BUTTON_ACTIVE if self.is_hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_BLACK, self.rect, 2)

        text_surface = font.render(self.text, True, COLOR_BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False


class Renderer:
    """Handles all rendering for the simulation."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Reactive Navigation Simulator")

        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

        # Create buttons
        button_y_top = WINDOW_HEIGHT - 110
        button_y_bottom = WINDOW_HEIGHT - 60
        button_height = 40
        self.buttons = {
            "algorithm": Button(10, button_y_top, 180, button_height, "Change Algorithm"),
            "start_stop": Button(10, button_y_bottom, 100, button_height, "Start/Stop"),
            "sonar": Button(120, button_y_bottom, 120, button_height, "Sonar On/Off"),
            "target": Button(250, button_y_bottom, 140, button_height, "Target Centric"),
            "tracking": Button(400, button_y_bottom, 120, button_height, "Track On/Off"),
            "save": Button(530, button_y_bottom, 90, button_height, "Save Path"),
            "trace": Button(630, button_y_bottom, 80, button_height, "Trace"),
            "quit": Button(720, button_y_bottom, 70, button_height, "Quit"),
        }

    def draw_environment(
        self, environment: Environment, show_sonar: bool = False, sonar_beams=None
    ) -> None:
        """Draw the environment including walls, obstacles, and target."""
        # Clear canvas area
        pygame.draw.rect(
            self.screen, COLOR_WHITE, (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        )

        # Draw walls
        for wall in environment.walls:
            pygame.draw.polygon(self.screen, COLOR_BLACK, wall.points)

        # Draw obstacles
        for obstacle in environment.obstacles:
            if isinstance(obstacle, Circle):
                pygame.draw.circle(
                    self.screen,
                    COLOR_OBSTACLE,
                    (int(obstacle.x), int(obstacle.y)),
                    int(obstacle.radius),
                )
                pygame.draw.circle(
                    self.screen,
                    COLOR_OBSTACLE_OUTLINE,
                    (int(obstacle.x), int(obstacle.y)),
                    int(obstacle.radius),
                    2,
                )
            elif isinstance(obstacle, Polygon):
                pygame.draw.polygon(self.screen, COLOR_OBSTACLE, obstacle.points)
                pygame.draw.polygon(self.screen, COLOR_OBSTACLE_OUTLINE, obstacle.points, 3)

        # Draw target
        pygame.draw.circle(
            self.screen,
            COLOR_TARGET,
            (int(environment.target.x), int(environment.target.y)),
            int(environment.target.radius),
        )

        # Draw sonar beams if enabled
        if show_sonar and sonar_beams:
            for beam in sonar_beams:
                x1, y1, x2, y2 = beam
                pygame.draw.line(
                    self.screen, COLOR_SONAR_LINE, (int(x1), int(y1)), (int(x2), int(y2)), 1
                )
                pygame.draw.aaline(
                    self.screen, COLOR_SONAR_LINE, (int(x1), int(y1)), (int(x2), int(y2))
                )

    def draw_robot(self, robot: Robot) -> None:
        """Draw the robot."""
        pygame.draw.circle(
            self.screen, COLOR_ROBOT, (int(robot.x), int(robot.y)), robot.radius
        )
        pygame.draw.circle(
            self.screen, COLOR_BLACK, (int(robot.x), int(robot.y)), robot.radius, 2
        )

    def draw_path_trace(self, robot: Robot) -> None:
        """Draw the robot's path trace."""
        if len(robot.path_trace) < 2:
            return

        # Draw lines connecting path points
        for i in range(len(robot.path_trace) - 1):
            start = (int(robot.path_trace[i][0]), int(robot.path_trace[i][1]))
            end = (int(robot.path_trace[i + 1][0]), int(robot.path_trace[i + 1][1]))
            pygame.draw.line(self.screen, COLOR_PATH_TRACE, start, end, 2)

        # Draw dots at each position
        for pos in robot.path_trace:
            pygame.draw.circle(
                self.screen, COLOR_PATH_TRACE, (int(pos[0]), int(pos[1])), 2
            )

    def draw_ui_panel(self, robot: Robot, state: SimulationState) -> None:
        """Draw the UI panel on the right side."""
        panel_x = CANVAS_WIDTH + 10
        panel_width = WINDOW_WIDTH - CANVAS_WIDTH - 20

        # Background
        pygame.draw.rect(
            self.screen,
            COLOR_UI_BG,
            (CANVAS_WIDTH, 0, WINDOW_WIDTH - CANVAS_WIDTH, CANVAS_HEIGHT),
        )

        y_pos = 20

        # Algorithm
        self.draw_text("Algorithm:", panel_x, y_pos, self.font_medium)
        y_pos += 25
        algo_name = robot.algorithm.get_name()
        # Wrap long algorithm names
        if len(algo_name) > 20:
            words = algo_name.split()
            line1 = " ".join(words[:len(words)//2])
            line2 = " ".join(words[len(words)//2:])
            self.draw_text(line1, panel_x, y_pos, self.font_small)
            y_pos += 20
            self.draw_text(line2, panel_x, y_pos, self.font_small)
            y_pos += 35
        else:
            self.draw_text(algo_name, panel_x, y_pos, self.font_small)
            y_pos += 50

        # Position
        self.draw_text("Position:", panel_x, y_pos, self.font_medium)
        y_pos += 25
        pos_text = f"({robot.x:.1f}, {robot.y:.1f})"
        self.draw_text(pos_text, panel_x, y_pos, self.font_small)
        y_pos += 40

        # Heading
        self.draw_text("Heading:", panel_x, y_pos, self.font_medium)
        y_pos += 25
        heading_text = f"{robot.heading:.1f}°"
        self.draw_text(heading_text, panel_x, y_pos, self.font_small)
        y_pos += 40

        # Target Centric
        self.draw_text("Target Centric:", panel_x, y_pos, self.font_medium)
        y_pos += 30
        self.draw_text(str(state.target_centric), panel_x, y_pos, self.font_small)
        y_pos += 50

        # Sonar
        self.draw_text("Sonar:", panel_x, y_pos, self.font_medium)
        y_pos += 30
        self.draw_text(str(state.sonar_enabled), panel_x, y_pos, self.font_small)
        y_pos += 50

        # Tracking
        self.draw_text("Tracking:", panel_x, y_pos, self.font_medium)
        y_pos += 30
        self.draw_text(str(state.tracking_enabled), panel_x, y_pos, self.font_small)
        y_pos += 50

        # Status
        if state.target_reached:
            self.draw_text("TARGET REACHED!", panel_x, y_pos, self.font_large, (0, 200, 0))

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: tuple = COLOR_UI_TEXT,
    ) -> None:
        """Draw text on the screen."""
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw_buttons(self) -> None:
        """Draw all UI buttons."""
        for button in self.buttons.values():
            button.draw(self.screen, self.font_small)

    def handle_button_events(self, event: pygame.event.Event) -> Optional[str]:
        """Handle button events. Returns button name if clicked."""
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None

    def update(self) -> None:
        """Update the display."""
        pygame.display.flip()

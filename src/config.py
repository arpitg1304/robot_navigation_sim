"""Configuration constants for the reactive navigation simulator."""

from dataclasses import dataclass
from typing import Tuple

# Window settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 700
FPS = 60

# Modern Color Palette
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

# Dark mode theme
COLOR_BG_DARK = (24, 24, 27)  # Almost black background
COLOR_BG_MEDIUM = (39, 39, 42)  # Medium dark
COLOR_BG_LIGHT = (63, 63, 70)  # Lighter dark
COLOR_TEXT_PRIMARY = (250, 250, 250)  # Off-white
COLOR_TEXT_SECONDARY = (161, 161, 170)  # Gray text
COLOR_ACCENT_PRIMARY = (99, 102, 241)  # Indigo
COLOR_ACCENT_SECONDARY = (139, 92, 246)  # Purple
COLOR_SUCCESS = (34, 197, 94)  # Green
COLOR_WARNING = (251, 191, 36)  # Amber
COLOR_DANGER = (239, 68, 68)  # Red

# Simulator elements
COLOR_CANVAS_BG = (245, 245, 247)  # Light gray for canvas
COLOR_ROBOT = (59, 130, 246)  # Blue robot
COLOR_TARGET = (251, 191, 36)  # Amber target
COLOR_TARGET_GLOW = (253, 224, 71)  # Yellow glow
COLOR_OBSTACLE = (71, 85, 105)  # Slate obstacles
COLOR_OBSTACLE_OUTLINE = (51, 65, 85)  # Darker slate
COLOR_PATH_TRACE = (139, 92, 246)  # Purple path
COLOR_SONAR_LINE = (34, 197, 94)  # Green sonar
COLOR_SONAR_BLOCKED = (239, 68, 68)  # Red for blocked

# UI Colors
COLOR_UI_BG = COLOR_BG_DARK
COLOR_UI_PANEL = COLOR_BG_MEDIUM
COLOR_UI_TEXT = COLOR_TEXT_PRIMARY
COLOR_UI_TEXT_DIM = COLOR_TEXT_SECONDARY
COLOR_BUTTON = COLOR_BG_LIGHT
COLOR_BUTTON_HOVER = (82, 82, 91)
COLOR_BUTTON_ACTIVE = COLOR_ACCENT_PRIMARY
COLOR_BUTTON_TEXT = COLOR_TEXT_PRIMARY
COLOR_DROPDOWN_BG = COLOR_BG_MEDIUM
COLOR_DROPDOWN_HOVER = COLOR_BG_LIGHT
COLOR_DROPDOWN_BORDER = (113, 113, 122)

# Robot settings
ROBOT_RADIUS = 10
ROBOT_STEP_SIZE = 20
ROBOT_START_X = 350
ROBOT_START_Y = 200

# Target settings
TARGET_RADIUS = 25
TARGET_DETECTION_DISTANCE = 20

# Sonar settings
SONAR_RANGE = 120  # Increased range for better obstacle detection
SONAR_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]  # 8 directions
SONAR_NUM_BEAMS = 8

# Obstacle settings
OBSTACLE_CIRCLE_RADIUS = 45

# Simulation settings
MOVE_INTERVAL = 5  # Frames between movements


@dataclass
class SimulationState:
    """Holds the current state of the simulation."""

    running: bool = False
    sonar_enabled: bool = True
    tracking_enabled: bool = False
    target_centric: bool = False
    target_reached: bool = False

#!/usr/bin/env python3
"""Interactive map editor for creating custom navigation maps.

Controls:
- Left Click + Drag: Create circular obstacle (radius = drag distance)
- P + Click: Polygon mode - click to add vertices, Enter to finish
- Right Click: Place/move target
- Click obstacle to select, Delete to remove
- S: Save map
- L: Load map
- C: Clear all
- ESC: Quit polygon mode / Quit editor
"""

import pygame
import sys
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Union

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import COLOR_CANVAS_BG, COLOR_OBSTACLE, COLOR_TARGET, COLOR_BLACK, COLOR_WHITE


class MapEditor:
    """Interactive map editor."""

    def __init__(self):
        pygame.init()
        self.width = 700
        self.height = 700
        self.ui_height = 120
        self.screen = pygame.display.set_mode((self.width, self.height + self.ui_height))
        pygame.display.set_caption("Map Editor - Enhanced")

        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

        # Map data - obstacles can be [x, y] for circles or [x1,y1,x2,y2,...] for polygons
        self.target = [500, 500]
        self.robot_start = [350, 200]  # Default robot start position
        self.obstacles = []
        self.selected_obstacle = None

        # Circle drawing state
        self.drawing_circle = False
        self.circle_start = None
        self.circle_current_pos = None

        # Polygon drawing state
        self.polygon_mode = False
        self.polygon_vertices = []

        # Map directory
        self.maps_dir = Path("maps")
        self.maps_dir.mkdir(exist_ok=True)

        # Default map name
        self.map_name = "custom_map"

        # Text input state
        self.editing_name = False
        self.name_input = self.map_name

        self.clock = pygame.time.Clock()
        self._print_instructions()

    def _print_instructions(self):
        """Print editor instructions."""
        print("=" * 60)
        print("Map Editor - Enhanced Version")
        print("=" * 60)
        print("Controls:")
        print("  Circle Mode (default):")
        print("    - Left Click + Drag: Create circle (radius = drag distance)")
        print("  Polygon Mode:")
        print("    - Press P: Enter polygon mode")
        print("    - Click: Add vertex")
        print("    - Enter: Complete polygon")
        print("    - ESC: Cancel polygon")
        print()
        print("  General:")
        print("    - Right Click: Place target")
        print("    - Middle Click: Set robot start position")
        print("    - Click obstacle + Delete: Remove obstacle")
        print("    - N: Edit map name")
        print("    - S: Save map")
        print("    - L: Load map (shows list of available maps)")
        print("    - C: Clear all obstacles")
        print("    - ESC: Quit (or cancel polygon/name edit mode)")
        print("=" * 60)

    def handle_events(self) -> bool:
        """Handle events. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                # Handle text input mode
                if self.editing_name:
                    if event.key == pygame.K_RETURN:
                        # Finish editing name
                        self.map_name = self.name_input if self.name_input.strip() else "custom_map"
                        self.editing_name = False
                        print(f"Map name set to: {self.map_name}")
                    elif event.key == pygame.K_ESCAPE:
                        # Cancel editing
                        self.name_input = self.map_name
                        self.editing_name = False
                        print("Name editing cancelled")
                    elif event.key == pygame.K_BACKSPACE:
                        # Delete character
                        self.name_input = self.name_input[:-1]
                    else:
                        # Add character (only allow alphanumeric, underscore, hyphen)
                        if event.unicode.isalnum() or event.unicode in ['_', '-']:
                            if len(self.name_input) < 30:  # Max length
                                self.name_input += event.unicode
                    continue

                # Normal key handling
                if event.key == pygame.K_ESCAPE:
                    if self.polygon_mode:
                        # Cancel polygon mode
                        self.polygon_mode = False
                        self.polygon_vertices = []
                        print("Polygon mode cancelled")
                    else:
                        # Quit editor
                        return False

                elif event.key == pygame.K_n:
                    # Edit map name
                    self.editing_name = True
                    self.name_input = self.map_name
                    print("Editing map name... (type and press Enter)")

                elif event.key == pygame.K_p:
                    # Enter polygon mode
                    self.polygon_mode = True
                    self.polygon_vertices = []
                    self.selected_obstacle = None
                    print("Polygon mode activated - click to add vertices, Enter to finish")

                elif event.key == pygame.K_RETURN:
                    if self.polygon_mode and len(self.polygon_vertices) >= 3:
                        # Complete polygon
                        polygon_coords = []
                        for v in self.polygon_vertices:
                            polygon_coords.extend(v)
                        self.obstacles.append(polygon_coords)
                        print(f"Polygon created with {len(self.polygon_vertices)} vertices")
                        self.polygon_mode = False
                        self.polygon_vertices = []

                elif event.key == pygame.K_s:
                    self.save_map()

                elif event.key == pygame.K_l:
                    self.show_map_selector()

                elif event.key == pygame.K_c:
                    self.clear_map()

                elif event.key == pygame.K_DELETE:
                    self.delete_selected()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Don't handle mouse clicks while editing name
                if self.editing_name:
                    continue

                x, y = event.pos
                if y >= self.height:  # Click in UI area
                    continue

                if event.button == 1:  # Left click
                    if self.polygon_mode:
                        # Add vertex to polygon
                        self.polygon_vertices.append([x, y])
                        print(f"Vertex {len(self.polygon_vertices)} added at ({x}, {y})")
                    else:
                        # Check if clicking existing obstacle
                        clicked_obs = self.find_obstacle_at(x, y)
                        if clicked_obs is not None:
                            self.selected_obstacle = clicked_obs
                            print(f"Selected obstacle {clicked_obs}")
                        else:
                            # Start drawing circle
                            self.drawing_circle = True
                            self.circle_start = (x, y)
                            self.circle_current_pos = (x, y)
                            self.selected_obstacle = None

                elif event.button == 2:  # Middle click
                    self.robot_start = [x, y]
                    print(f"Robot start position set to ({x}, {y})")

                elif event.button == 3:  # Right click
                    self.target = [x, y]
                    print(f"Target moved to ({x}, {y})")

            elif event.type == pygame.MOUSEMOTION:
                if self.drawing_circle:
                    # Update circle preview
                    x, y = event.pos
                    self.circle_current_pos = (x, min(y, self.height - 1))

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.drawing_circle:
                    x, y = event.pos
                    if y < self.height and self.circle_start:
                        # Calculate radius from drag distance
                        dx = x - self.circle_start[0]
                        dy = y - self.circle_start[1]
                        radius = int((dx**2 + dy**2)**0.5)

                        # Only create if radius is reasonable (at least 10 pixels)
                        if radius >= 10:
                            self.obstacles.append(list(self.circle_start))
                            print(f"Circle obstacle created at {self.circle_start} (dragged {radius}px)")
                        else:
                            # Small drag = default circle
                            self.obstacles.append(list(self.circle_start))
                            print(f"Circle obstacle created at {self.circle_start}")

                    self.drawing_circle = False
                    self.circle_start = None
                    self.circle_current_pos = None

        return True

    def find_obstacle_at(self, x: int, y: int) -> Optional[int]:
        """Find obstacle at given position."""
        for i, obs in enumerate(self.obstacles):
            if len(obs) == 2:  # Circle
                dist = ((x - obs[0])**2 + (y - obs[1])**2)**0.5
                if dist <= 45:
                    return i
            else:  # Polygon
                # Simple point-in-polygon check (bounding box for simplicity)
                points = [(obs[j], obs[j+1]) for j in range(0, len(obs), 2)]
                min_x = min(p[0] for p in points)
                max_x = max(p[0] for p in points)
                min_y = min(p[1] for p in points)
                max_y = max(p[1] for p in points)

                if min_x <= x <= max_x and min_y <= y <= max_y:
                    return i
        return None

    def delete_selected(self):
        """Delete currently selected obstacle."""
        if self.selected_obstacle is not None:
            obs = self.obstacles.pop(self.selected_obstacle)
            obs_type = "circle" if len(obs) == 2 else "polygon"
            print(f"Deleted {obs_type} obstacle")
            self.selected_obstacle = None

    def get_available_maps(self):
        """Get list of available map names."""
        if not self.maps_dir.exists():
            return []

        maps = []
        for map_folder in self.maps_dir.iterdir():
            if map_folder.is_dir():
                target_file = map_folder / "target.npy"
                obstacles_file = map_folder / "obstacles.npy"
                if target_file.exists() and obstacles_file.exists():
                    maps.append(map_folder.name)

        return sorted(maps)

    def show_map_selector(self):
        """Show console-based map selector."""
        available_maps = self.get_available_maps()

        if not available_maps:
            print("=" * 60)
            print("No maps found!")
            print("Create a new map first with 'N' (name) and 'S' (save)")
            print("=" * 60)
            return

        print("\n" + "=" * 60)
        print("Available Maps:")
        print("=" * 60)
        for i, map_name in enumerate(available_maps, 1):
            print(f"  {i}. {map_name}")
        print()
        print("Enter map number to load (or 0 to cancel):")
        print("=" * 60)

        # Simple console input for map selection
        try:
            choice = input("Map number: ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if choice_num == 0:
                    print("Load cancelled")
                    return
                elif 1 <= choice_num <= len(available_maps):
                    selected_map = available_maps[choice_num - 1]
                    self.map_name = selected_map
                    self.load_map()
                else:
                    print(f"Invalid choice: {choice_num}")
            else:
                print("Invalid input")
        except (EOFError, KeyboardInterrupt):
            print("\nLoad cancelled")

    def save_map(self):
        """Save current map to files."""
        target_data = np.array([self.target])
        robot_start_data = np.array([self.robot_start])
        obstacles_data = np.array(self.obstacles, dtype=object)

        # Create map folder
        map_folder = self.maps_dir / self.map_name
        map_folder.mkdir(exist_ok=True)

        target_file = map_folder / "target.npy"
        start_file = map_folder / "start.npy"
        obstacles_file = map_folder / "obstacles.npy"

        np.save(target_file, target_data)
        np.save(start_file, robot_start_data)
        np.save(obstacles_file, obstacles_data, allow_pickle=True)

        circles = sum(1 for obs in self.obstacles if len(obs) == 2)
        polygons = len(self.obstacles) - circles

        print("=" * 60)
        print(f"✓ Map saved as '{self.map_name}'")
        print(f"  Location: {map_folder}/")
        print(f"  Robot start: ({self.robot_start[0]}, {self.robot_start[1]})")
        print(f"  Total obstacles: {len(self.obstacles)} ({circles} circles, {polygons} polygons)")
        print("=" * 60)

    def load_map(self):
        """Load map from files."""
        map_folder = self.maps_dir / self.map_name
        target_file = map_folder / "target.npy"
        start_file = map_folder / "start.npy"
        obstacles_file = map_folder / "obstacles.npy"

        if target_file.exists() and obstacles_file.exists():
            target_data = np.load(target_file, allow_pickle=True)
            obstacles_data = np.load(obstacles_file, allow_pickle=True)

            self.target = list(target_data[0])
            self.obstacles = [list(obs) for obs in obstacles_data]

            # Load robot start position if it exists, otherwise use default
            if start_file.exists():
                start_data = np.load(start_file, allow_pickle=True)
                self.robot_start = list(start_data[0])
            else:
                self.robot_start = [350, 200]  # Default
                print("  Note: No start position found, using default (350, 200)")

            self.selected_obstacle = None

            circles = sum(1 for obs in self.obstacles if len(obs) == 2)
            polygons = len(self.obstacles) - circles

            print("=" * 60)
            print(f"✓ Map loaded from '{self.map_name}'")
            print(f"  Location: {map_folder}/")
            print(f"  Robot start: ({self.robot_start[0]}, {self.robot_start[1]})")
            print(f"  Total obstacles: {len(self.obstacles)} ({circles} circles, {polygons} polygons)")
            print("=" * 60)
        else:
            print(f"✗ Map '{self.map_name}' not found at {map_folder}/")

    def clear_map(self):
        """Clear all obstacles."""
        self.obstacles = []
        self.selected_obstacle = None
        self.polygon_vertices = []
        self.polygon_mode = False
        print("Map cleared")

    def draw(self):
        """Draw the editor."""
        # Clear screen
        self.screen.fill(COLOR_WHITE)

        # Draw canvas area
        canvas_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.screen, COLOR_CANVAS_BG, canvas_rect)

        # Draw grid
        grid_color = (220, 220, 225)
        for x in range(0, self.width, 50):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), 1)

        # Draw obstacles
        for i, obs in enumerate(self.obstacles):
            is_selected = (i == self.selected_obstacle)

            if len(obs) == 2:  # Circle
                color = (255, 100, 100) if is_selected else COLOR_OBSTACLE
                pygame.draw.circle(self.screen, color, (int(obs[0]), int(obs[1])), 45)
                pygame.draw.circle(self.screen, COLOR_BLACK, (int(obs[0]), int(obs[1])), 45, 2)
            else:  # Polygon
                points = [(obs[j], obs[j+1]) for j in range(0, len(obs), 2)]
                color = (255, 100, 100) if is_selected else COLOR_OBSTACLE
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, COLOR_BLACK, points, 2)

        # Draw circle preview while dragging
        if self.drawing_circle and self.circle_start and self.circle_current_pos:
            dx = self.circle_current_pos[0] - self.circle_start[0]
            dy = self.circle_current_pos[1] - self.circle_start[1]
            radius = max(10, int((dx**2 + dy**2)**0.5))

            # Draw preview circle with transparency effect
            preview_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(
                preview_surface,
                (*COLOR_OBSTACLE, 100),  # Semi-transparent
                self.circle_start,
                radius,
            )
            pygame.draw.circle(
                preview_surface,
                COLOR_BLACK,
                self.circle_start,
                radius,
                2
            )
            self.screen.blit(preview_surface, (0, 0))

            # Draw line showing radius
            pygame.draw.line(
                self.screen,
                (255, 255, 0),
                self.circle_start,
                self.circle_current_pos,
                2
            )

        # Draw polygon in progress
        if self.polygon_mode and len(self.polygon_vertices) > 0:
            # Draw vertices
            for vertex in self.polygon_vertices:
                pygame.draw.circle(self.screen, (0, 255, 0), vertex, 5)

            # Draw edges
            if len(self.polygon_vertices) > 1:
                pygame.draw.lines(
                    self.screen,
                    (0, 255, 0),
                    False,
                    self.polygon_vertices,
                    2
                )

            # Draw line to mouse position
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] < self.height:
                pygame.draw.line(
                    self.screen,
                    (0, 255, 0, 128),
                    self.polygon_vertices[-1],
                    mouse_pos,
                    1
                )

            # Draw closing line preview if enough vertices
            if len(self.polygon_vertices) >= 3:
                pygame.draw.line(
                    self.screen,
                    (255, 255, 0),
                    self.polygon_vertices[-1],
                    self.polygon_vertices[0],
                    1
                )

        # Draw robot start position
        pygame.draw.circle(
            self.screen, (59, 130, 246), (int(self.robot_start[0]), int(self.robot_start[1])), 12
        )
        pygame.draw.circle(
            self.screen, COLOR_BLACK, (int(self.robot_start[0]), int(self.robot_start[1])), 12, 2
        )
        pygame.draw.circle(
            self.screen, COLOR_WHITE, (int(self.robot_start[0]), int(self.robot_start[1])), 3
        )

        # Draw target
        pygame.draw.circle(
            self.screen, COLOR_TARGET, (int(self.target[0]), int(self.target[1])), 25
        )
        pygame.draw.circle(
            self.screen, (255, 255, 0), (int(self.target[0]), int(self.target[1])), 15
        )
        pygame.draw.circle(
            self.screen, COLOR_WHITE, (int(self.target[0]), int(self.target[1])), 4
        )

        # Draw UI panel
        ui_rect = pygame.Rect(0, self.height, self.width, self.ui_height)
        pygame.draw.rect(self.screen, (40, 40, 45), ui_rect)

        # Draw title and mode indicator
        mode_text = "POLYGON MODE" if self.polygon_mode else "CIRCLE MODE"
        mode_color = (100, 255, 100) if self.polygon_mode else (100, 200, 255)

        title = self.font_large.render("Map Editor", True, COLOR_WHITE)
        self.screen.blit(title, (20, self.height + 10))

        mode = self.font_medium.render(mode_text, True, mode_color)
        self.screen.blit(mode, (200, self.height + 15))

        # Draw stats
        circles = sum(1 for obs in self.obstacles if len(obs) == 2)
        polygons = len(self.obstacles) - circles

        stats = self.font_small.render(
            f"Obstacles: {len(self.obstacles)} ({circles} circles, {polygons} polygons) | Target: ({self.target[0]}, {self.target[1]})",
            True,
            (200, 200, 200),
        )
        self.screen.blit(stats, (20, self.height + 50))

        # Draw polygon progress
        if self.polygon_mode:
            poly_progress = self.font_small.render(
                f"Polygon vertices: {len(self.polygon_vertices)} (need 3+ to complete, press Enter)",
                True,
                (150, 255, 150),
            )
            self.screen.blit(poly_progress, (20, self.height + 70))
        else:
            # Draw controls
            controls = self.font_small.render(
                "Drag: Circle | P: Polygon | RClick: Target | Del: Remove | N: Name | S: Save | L: Load",
                True,
                (150, 150, 150),
            )
            self.screen.blit(controls, (20, self.height + 70))

        # Draw map name input
        if self.editing_name:
            # Show text input box
            name_bg = pygame.Rect(20, self.height + 90, 400, 25)
            pygame.draw.rect(self.screen, (60, 60, 65), name_bg)
            pygame.draw.rect(self.screen, (100, 200, 255), name_bg, 2)

            name_text = self.font_small.render(
                f"Map name: {self.name_input}_",
                True,
                (255, 255, 255),
            )
            self.screen.blit(name_text, (25, self.height + 95))

            hint_text = self.font_small.render(
                "(Press Enter to confirm, ESC to cancel)",
                True,
                (150, 150, 150),
            )
            self.screen.blit(hint_text, (430, self.height + 95))
        else:
            # Show current map name
            hint = self.font_small.render(
                f"Map name: {self.map_name} (press N to edit, S to save)",
                True,
                (120, 120, 120),
            )
            self.screen.blit(hint, (20, self.height + 95))

        pygame.display.flip()

    def run(self):
        """Main loop."""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        print("Map editor closed")


def main():
    """Entry point."""
    editor = MapEditor()
    editor.run()


if __name__ == "__main__":
    main()

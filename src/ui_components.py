"""Modern UI components for the simulator."""

import pygame
from typing import List, Tuple, Optional, Callable
from src.config import *


class ModernButton:
    """Modern styled button with hover and click effects."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        icon: Optional[str] = None,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.is_hovered = False
        self.is_pressed = False
        self.is_active = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the modern button with gradient and effects."""
        # Determine color based on state
        if self.is_active:
            color = COLOR_ACCENT_PRIMARY
            text_color = COLOR_WHITE
        elif self.is_pressed:
            color = COLOR_BUTTON_HOVER
            text_color = COLOR_TEXT_PRIMARY
        elif self.is_hovered:
            color = COLOR_BUTTON_HOVER
            text_color = COLOR_TEXT_PRIMARY
        else:
            color = COLOR_BUTTON
            text_color = COLOR_BUTTON_TEXT

        # Draw button background with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # Draw subtle border
        border_color = (
            COLOR_ACCENT_SECONDARY if self.is_active else (100, 100, 110)
        )
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        # Draw text
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.is_hovered:
                self.is_pressed = False
                return True
            self.is_pressed = False
        return False


class Dropdown:
    """Modern dropdown menu for selecting options."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        options: List[str],
        selected_index: int = 0,
        on_select: Optional[Callable[[int], None]] = None,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.is_open = False
        self.is_hovered = False
        self.hovered_option = -1
        self.on_select = on_select

        # Calculate dropdown list dimensions
        self.item_height = height
        self.list_rect = pygame.Rect(
            x, y + height, width, len(options) * self.item_height
        )

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the dropdown menu."""
        # Draw main dropdown button
        bg_color = COLOR_DROPDOWN_HOVER if self.is_hovered else COLOR_DROPDOWN_BG
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(
            screen, COLOR_DROPDOWN_BORDER, self.rect, 2, border_radius=8
        )

        # Draw selected text
        selected_text = self.options[self.selected_index]
        # Truncate long text
        if len(selected_text) > 25:
            selected_text = selected_text[:22] + "..."

        text_surface = font.render(selected_text, True, COLOR_TEXT_PRIMARY)
        text_rect = text_surface.get_rect(
            midleft=(self.rect.x + 12, self.rect.centery)
        )
        screen.blit(text_surface, text_rect)

        # Draw arrow indicator
        arrow = "▼" if not self.is_open else "▲"
        arrow_surface = font.render(arrow, True, COLOR_TEXT_SECONDARY)
        arrow_rect = arrow_surface.get_rect(
            midright=(self.rect.right - 12, self.rect.centery)
        )
        screen.blit(arrow_surface, arrow_rect)

        # Draw dropdown list if open
        if self.is_open:
            # Draw dropdown background with shadow effect
            shadow_rect = self.list_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(
                screen, (0, 0, 0, 100), shadow_rect, border_radius=8
            )

            pygame.draw.rect(
                screen, COLOR_DROPDOWN_BG, self.list_rect, border_radius=8
            )
            pygame.draw.rect(
                screen,
                COLOR_DROPDOWN_BORDER,
                self.list_rect,
                2,
                border_radius=8,
            )

            # Draw each option
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.list_rect.x,
                    self.list_rect.y + i * self.item_height,
                    self.list_rect.width,
                    self.item_height,
                )

                # Highlight hovered or selected option
                if i == self.hovered_option:
                    pygame.draw.rect(
                        screen, COLOR_DROPDOWN_HOVER, option_rect, border_radius=6
                    )
                elif i == self.selected_index:
                    pygame.draw.rect(
                        screen,
                        COLOR_BG_LIGHT,
                        option_rect,
                        border_radius=6,
                    )

                # Draw option text
                option_text = option
                if len(option_text) > 30:
                    option_text = option_text[:27] + "..."

                text_color = (
                    COLOR_ACCENT_PRIMARY
                    if i == self.selected_index
                    else COLOR_TEXT_PRIMARY
                )
                option_surface = font.render(option_text, True, text_color)
                option_text_rect = option_surface.get_rect(
                    midleft=(option_rect.x + 12, option_rect.centery)
                )
                screen.blit(option_surface, option_text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if selection changed."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

            if self.is_open:
                # Check which option is hovered
                self.hovered_option = -1
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(
                        self.list_rect.x,
                        self.list_rect.y + i * self.item_height,
                        self.list_rect.width,
                        self.item_height,
                    )
                    if option_rect.collidepoint(event.pos):
                        self.hovered_option = i
                        break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and not self.is_open:
                # Open dropdown
                self.is_open = True
                return False
            elif self.is_open:
                # Check if clicked on an option
                if self.hovered_option >= 0:
                    old_index = self.selected_index
                    self.selected_index = self.hovered_option
                    self.is_open = False
                    if self.on_select and old_index != self.selected_index:
                        self.on_select(self.selected_index)
                    return old_index != self.selected_index
                else:
                    # Clicked outside, close dropdown
                    self.is_open = False

        return False

    def set_options(self, options: List[str], selected_index: int = 0) -> None:
        """Update the options list."""
        self.options = options
        self.selected_index = selected_index
        self.list_rect.height = len(options) * self.item_height


class ToggleSwitch:
    """Modern toggle switch component."""

    def __init__(self, x: int, y: int, width: int, height: int, label: str) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.is_on = False
        self.is_hovered = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the toggle switch."""
        # Draw label
        label_surface = font.render(self.label, True, COLOR_TEXT_SECONDARY)
        label_rect = label_surface.get_rect(midleft=(self.rect.x, self.rect.centery))
        screen.blit(label_surface, label_rect)

        # Switch dimensions
        switch_width = 50
        switch_height = 26
        switch_x = self.rect.right - switch_width
        switch_y = self.rect.centery - switch_height // 2
        switch_rect = pygame.Rect(switch_x, switch_y, switch_width, switch_height)

        # Draw switch background
        bg_color = COLOR_SUCCESS if self.is_on else COLOR_BG_LIGHT
        pygame.draw.rect(screen, bg_color, switch_rect, border_radius=13)

        # Draw switch knob
        knob_radius = 10
        knob_x = switch_x + switch_width - 13 if self.is_on else switch_x + 13
        knob_y = switch_y + switch_height // 2
        pygame.draw.circle(screen, COLOR_WHITE, (knob_x, knob_y), knob_radius)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if toggled."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_on = not self.is_on
                return True
        return False


class StatCard:
    """Modern stat display card."""

    def __init__(
        self, x: int, y: int, width: int, height: int, label: str, value: str
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.value = value

    def draw(
        self, screen: pygame.Surface, label_font: pygame.font.Font, value_font: pygame.font.Font
    ) -> None:
        """Draw the stat card."""
        # Draw card background
        pygame.draw.rect(screen, COLOR_UI_PANEL, self.rect, border_radius=8)
        pygame.draw.rect(
            screen, COLOR_BG_LIGHT, self.rect, 1, border_radius=8
        )

        # Draw label
        label_surface = label_font.render(self.label, True, COLOR_TEXT_SECONDARY)
        label_rect = label_surface.get_rect(
            midtop=(self.rect.centerx, self.rect.y + 8)
        )
        screen.blit(label_surface, label_rect)

        # Draw value
        value_surface = value_font.render(str(self.value), True, COLOR_TEXT_PRIMARY)
        value_rect = value_surface.get_rect(
            midbottom=(self.rect.centerx, self.rect.bottom - 8)
        )
        screen.blit(value_surface, value_rect)

    def update_value(self, value: str) -> None:
        """Update the displayed value."""
        self.value = value

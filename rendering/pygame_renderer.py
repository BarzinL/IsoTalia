"""
PyGame rendering backend.
Handles all PyGame-specific rendering logic.
"""

import pygame
from typing import List, Dict
from .isometric import IsometricConverter, Camera
from .sprite_manager import SpriteManager


class PyGameRenderer:
    """
    PyGame-specific renderer.
    Converts framework-agnostic render data into PyGame visuals.
    """

    def __init__(self, screen_width: int = 1280, screen_height: int = 720,
                 tile_width: int = 32, tile_height: int = 16):
        """
        Initialize PyGame renderer.

        Args:
            screen_width: Window width in pixels
            screen_height: Window height in pixels
            tile_width: Tile width in pixels
            tile_height: Tile height in pixels
        """
        pygame.init()

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Create display
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("IsoTalia")

        # Rendering utilities
        self.iso_converter = IsometricConverter(tile_width, tile_height)
        self.camera = Camera(screen_width, screen_height, tile_width, tile_height)
        self.sprite_manager = SpriteManager()

        # Background color (dark wasteland)
        self.bg_color = (30, 30, 35)

        # Font for debug info
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Debug mode
        self.show_debug = False

    def render(self, render_data: dict):
        """
        Render a frame using render data from game state.

        Args:
            render_data: Dict containing tiles, entities, camera info
        """
        # Clear screen
        self.screen.fill(self.bg_color)

        # Collect all renderable objects
        render_queue = []

        # Add tiles to render queue
        for tile_data in render_data['tiles']:
            render_queue.append({
                'type': 'tile',
                'data': tile_data,
                'sort_key': self.iso_converter.get_depth_sort_key(
                    tile_data['x'], tile_data['y'], tile_data['z'], layer=0
                )
            })

        # Add entities to render queue
        for entity_data in render_data['entities']:
            render_queue.append({
                'type': 'entity',
                'data': entity_data,
                'sort_key': self.iso_converter.get_depth_sort_key(
                    entity_data['x'], entity_data['y'], entity_data['z'],
                    layer=entity_data['layer']
                )
            })

        # Sort by depth (painter's algorithm)
        render_queue.sort(key=lambda item: item['sort_key'])

        # Render all objects
        for item in render_queue:
            if item['type'] == 'tile':
                self._render_tile(item['data'])
            elif item['type'] == 'entity':
                self._render_entity(item['data'])

        # Render debug info if enabled
        if self.show_debug:
            self._render_debug_info(render_data)

        # Update display
        pygame.display.flip()

    def _render_tile(self, tile_data: dict):
        """Render a single tile."""
        world_x = tile_data['x']
        world_y = tile_data['y']
        world_z = tile_data['z']
        texture_id = tile_data['texture_id']

        # Get screen position
        screen_x, screen_y = self.camera.world_to_screen_with_camera(
            world_x, world_y, world_z, self.iso_converter
        )

        # Get sprite
        sprite = self.sprite_manager.get_sprite(texture_id, self.tile_width, self.tile_height)

        # Center sprite on position
        rect = sprite.get_rect()
        rect.center = (screen_x, screen_y)

        # Render
        self.screen.blit(sprite, rect)

    def _render_entity(self, entity_data: dict):
        """Render a single entity."""
        world_x = entity_data['x']
        world_y = entity_data['y']
        world_z = entity_data['z']
        texture_id = entity_data['texture_id']
        offset_x = entity_data.get('offset_x', 0)
        offset_y = entity_data.get('offset_y', 0)

        # Get screen position
        screen_x, screen_y = self.camera.world_to_screen_with_camera(
            world_x, world_y, world_z, self.iso_converter
        )

        # Apply entity offset
        screen_x += offset_x
        screen_y += offset_y

        # Get sprite (entities use tile dimensions for now)
        sprite = self.sprite_manager.get_sprite(texture_id, self.tile_width, self.tile_height)

        # Position sprite (bottom-center anchor for entities)
        rect = sprite.get_rect()
        rect.midbottom = (screen_x, screen_y)

        # Render
        self.screen.blit(sprite, rect)

    def _render_debug_info(self, render_data: dict):
        """Render debug information overlay."""
        debug_lines = [
            f"Camera: ({self.camera.x:.1f}, {self.camera.y:.1f})",
            f"Tiles: {len(render_data['tiles'])}",
            f"Entities: {len(render_data['entities'])}",
            f"Game Time: {render_data['game_time']:.1f}s",
        ]

        y_offset = 10
        for line in debug_lines:
            text_surface = self.small_font.render(line, True, (255, 255, 0))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 20
            
        # Render viewport bounds visualization
        self._render_debug_bounds(render_data)
        
    def _render_debug_bounds(self, render_data: dict):
        """Render debug visualization of viewport bounds."""
        min_x, min_y, max_x, max_y = self.camera.get_visible_bounds()
        
        # Draw corners of the calculated bounds
        corners = [
            (min_x, min_y), (max_x, min_y),
            (max_x, max_y), (min_x, max_y)
        ]
        
        for world_x, world_y in corners:
            screen_x, screen_y = self.camera.world_to_screen_with_camera(
                world_x, world_y, 0, self.iso_converter
            )
            pygame.draw.circle(self.screen, (255, 0, 0), (int(screen_x), int(screen_y)), 5)
            
        # Draw bounds rectangle
        corner_points = []
        for world_x, world_y in corners:
            screen_x, screen_y = self.camera.world_to_screen_with_camera(
                world_x, world_y, 0, self.iso_converter
            )
            corner_points.append((int(screen_x), int(screen_y)))
            
        if len(corner_points) >= 3:
            pygame.draw.polygon(self.screen, (255, 0, 0), corner_points, 1)

    def center_camera_on(self, world_x: int, world_y: int):
        """Center camera on world position."""
        self.camera.center_on(world_x, world_y)

    def move_camera(self, dx: float, dy: float):
        """Move camera by delta."""
        self.camera.move(dx, dy)

    def toggle_debug(self):
        """Toggle debug overlay."""
        self.show_debug = not self.show_debug

    def shutdown(self):
        """Clean shutdown."""
        pygame.quit()

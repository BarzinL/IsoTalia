"""
Sprite and asset management.
Handles loading, caching, and generating placeholder sprites.
"""

import pygame
from typing import Dict, Tuple, Optional
from pathlib import Path


class SpriteManager:
    """
    Manages sprite loading and caching.
    Generates placeholder sprites for MVP.
    """

    def __init__(self, assets_path: str = "assets/sprites"):
        self.assets_path = Path(assets_path)
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        self._placeholder_cache: Dict[str, pygame.Surface] = {}

        # Color scheme for placeholder tiles (post-apocalyptic palette)
        self.tile_colors = {
            'void': (20, 20, 20),
            'wasteland_dirt': (139, 119, 101),
            'cracked_pavement': (105, 105, 105),
            'rubble': (128, 128, 128),
            'toxic_water': (50, 150, 50),
        }

        self.entity_colors = {
            'player': (255, 200, 50),  # Yellowish
        }

    def get_sprite(self, texture_id: str, tile_width: int = 32, tile_height: int = 16) -> pygame.Surface:
        """
        Get sprite by texture ID.
        Returns cached sprite or generates placeholder if not found.
        """
        # Check cache first
        cache_key = f"{texture_id}_{tile_width}x{tile_height}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]

        # Try to load from file
        sprite_path = self.assets_path / f"{texture_id}.png"
        if sprite_path.exists():
            sprite = pygame.image.load(str(sprite_path)).convert_alpha()
            self._sprite_cache[cache_key] = sprite
            return sprite

        # Generate placeholder
        return self._get_placeholder(texture_id, tile_width, tile_height)

    def _get_placeholder(self, texture_id: str, width: int, height: int) -> pygame.Surface:
        """Generate a placeholder sprite."""
        cache_key = f"ph_{texture_id}_{width}x{height}"

        if cache_key in self._placeholder_cache:
            return self._placeholder_cache[cache_key]

        # Determine if it's a tile or entity
        if texture_id in self.tile_colors:
            sprite = self._generate_tile_placeholder(texture_id, width, height)
        elif texture_id in self.entity_colors:
            sprite = self._generate_entity_placeholder(texture_id, width, height)
        else:
            # Unknown - create debug sprite
            sprite = self._generate_debug_sprite(texture_id, width, height)

        self._placeholder_cache[cache_key] = sprite
        return sprite

    def _generate_tile_placeholder(self, texture_id: str, width: int, height: int) -> pygame.Surface:
        """Generate a diamond-shaped tile placeholder."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        color = self.tile_colors.get(texture_id, (100, 100, 100))

        # Draw diamond shape
        points = [
            (width // 2, 0),           # Top
            (width, height // 2),      # Right
            (width // 2, height),      # Bottom
            (0, height // 2),          # Left
        ]

        # Fill
        pygame.draw.polygon(surface, color, points)

        # Outline
        darker = tuple(max(0, c - 30) for c in color)
        pygame.draw.polygon(surface, darker, points, 1)

        return surface

    def _generate_entity_placeholder(self, texture_id: str, width: int, height: int) -> pygame.Surface:
        """Generate an entity placeholder sprite."""
        # Entities are taller than tiles
        entity_height = height * 2
        surface = pygame.Surface((width, entity_height), pygame.SRCALPHA)
        color = self.entity_colors.get(texture_id, (200, 200, 200))

        # Draw simple character shape (rectangle with head)
        # Body
        body_rect = pygame.Rect(width // 4, entity_height // 2, width // 2, entity_height // 3)
        pygame.draw.rect(surface, color, body_rect)

        # Head
        head_center = (width // 2, entity_height // 3)
        head_radius = width // 4
        pygame.draw.circle(surface, color, head_center, head_radius)

        # Outline
        pygame.draw.rect(surface, (0, 0, 0), body_rect, 1)
        pygame.draw.circle(surface, (0, 0, 0), head_center, head_radius, 1)

        return surface

    def _generate_debug_sprite(self, texture_id: str, width: int, height: int) -> pygame.Surface:
        """Generate a debug sprite with text label."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Magenta background for visibility
        pygame.draw.rect(surface, (255, 0, 255), surface.get_rect())

        # Try to add text label (requires font)
        try:
            font = pygame.font.Font(None, 12)
            # Truncate texture_id if too long
            label = texture_id[:6] if len(texture_id) > 6 else texture_id
            text = font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            surface.blit(text, text_rect)
        except:
            pass

        return surface

    def clear_cache(self):
        """Clear sprite cache."""
        self._sprite_cache.clear()
        self._placeholder_cache.clear()

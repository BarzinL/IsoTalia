"""
Movement system - handles grid-based entity movement.
Framework-agnostic movement logic.
"""

from typing import Optional, Tuple
from ..entities.components import Position, Movement
from ..entities.entity import Entity, EntityManager
from ..world.tile_map import TileMap


class MovementSystem:
    """
    Handles grid-locked movement for entities.
    Validates movement against terrain and collision.
    """

    def __init__(self, tile_map: TileMap, entity_manager: EntityManager):
        self.tile_map = tile_map
        self.entity_manager = entity_manager

    def can_move_to(self, entity: Entity, target_x: int, target_y: int) -> bool:
        """
        Check if an entity can move to target position.
        Validates terrain walkability and entity collision.
        """
        # Check map bounds
        if not self.tile_map.is_valid_position(target_x, target_y):
            return False

        # Check if tile is walkable
        if not self.tile_map.is_walkable(target_x, target_y):
            # Check if entity can fly or swim
            movement = entity.get_component(Movement)
            if movement:
                tile = self.tile_map.get_tile(target_x, target_y)
                if tile and tile.tile_type.id == "toxic_water" and movement.can_swim:
                    return True
                if movement.can_fly:
                    return True
            return False

        # Check for entity collision (optional - could allow stacking)
        # For now, we'll allow multiple entities on same tile

        return True

    def move_entity(self, entity: Entity, dx: int, dy: int) -> bool:
        """
        Move entity by delta (grid-locked).
        dx, dy should be -1, 0, or 1.
        Returns True if movement succeeded.
        """
        pos = entity.get_component(Position)
        if not pos:
            return False

        target_x = pos.x + dx
        target_y = pos.y + dy

        if self.can_move_to(entity, target_x, target_y):
            pos.x = target_x
            pos.y = target_y
            return True

        return False

    def move_entity_to(self, entity: Entity, x: int, y: int) -> bool:
        """
        Move entity to absolute position.
        Returns True if movement succeeded.
        """
        pos = entity.get_component(Position)
        if not pos:
            return False

        if self.can_move_to(entity, x, y):
            pos.x = x
            pos.y = y
            return True

        return False

    def get_movement_direction(self, command: str) -> Tuple[int, int]:
        """
        Convert movement command to direction delta.
        Returns (dx, dy) tuple.
        """
        directions = {
            'move_north': (0, -1),
            'move_south': (0, 1),
            'move_east': (1, 0),
            'move_west': (-1, 0),
            'move_northeast': (1, -1),
            'move_northwest': (-1, -1),
            'move_southeast': (1, 1),
            'move_southwest': (-1, 1),
        }
        return directions.get(command, (0, 0))

    def process_movement_command(self, entity: Entity, command: str) -> bool:
        """
        Process a movement command for an entity.
        Returns True if movement succeeded.
        """
        dx, dy = self.get_movement_direction(command)
        if dx != 0 or dy != 0:
            return self.move_entity(entity, dx, dy)
        return False

"""
Interaction system - handles tool usage, digging, harvesting.
Framework-agnostic interaction logic.
"""

from typing import List, Optional
from ..entities.components import Position, Tool, Inventory
from ..entities.entity import Entity
from ..world.tile_map import TileMap


class InteractionSystem:
    """
    Handles entity interactions with the world.
    Digging, harvesting, building, etc.
    """

    def __init__(self, tile_map: TileMap):
        self.tile_map = tile_map

    def dig_at_position(self, entity: Entity, target_x: int, target_y: int) -> dict:
        """
        Dig/harvest at target position using entity's tool.
        Returns dict with success status and dropped resources.
        """
        result = {
            'success': False,
            'resources': [],
            'message': ''
        }

        # Check if entity has a tool
        tool = entity.get_component(Tool)
        if not tool:
            result['message'] = "No tool equipped"
            return result

        # Check if position is valid
        if not self.tile_map.is_valid_position(target_x, target_y):
            result['message'] = "Invalid position"
            return result

        # Get the tile
        tile = self.tile_map.get_tile(target_x, target_y)
        if not tile:
            result['message'] = "No tile at position"
            return result

        # Check if tile can be dug
        if tile.hardness == 0:
            result['message'] = "Cannot dig this tile"
            return result

        # Check if tool is strong enough (optional check)
        if tool.power < tile.hardness:
            result['message'] = "Tool not strong enough"
            # Could allow digging but take multiple hits
            # For MVP, we'll allow it anyway

        # Use the tool (reduces durability)
        tool_still_works = tool.use()

        # Dig the tile
        drops = self.tile_map.dig_tile(target_x, target_y)

        # Add resources to entity inventory if it has one
        inventory = entity.get_component(Inventory)
        if inventory:
            for item in drops:
                inventory.add_item(item)

        result['success'] = True
        result['resources'] = drops
        if not tool_still_works:
            result['message'] = "Tool broke!"
        else:
            result['message'] = f"Dug tile, found {len(drops)} resources"

        return result

    def dig_adjacent(self, entity: Entity, direction: str) -> dict:
        """
        Dig in a direction relative to entity position.
        Direction: 'north', 'south', 'east', 'west'
        """
        pos = entity.get_component(Position)
        if not pos:
            return {'success': False, 'message': 'Entity has no position'}

        # Calculate target position based on direction
        direction_map = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }

        dx, dy = direction_map.get(direction, (0, 0))
        target_x = pos.x + dx
        target_y = pos.y + dy

        return self.dig_at_position(entity, target_x, target_y)

    def place_tile(self, entity: Entity, target_x: int, target_y: int,
                   tile_type_id: str) -> dict:
        """
        Place a tile at target position.
        Could require entity to have the tile in inventory.
        """
        result = {
            'success': False,
            'message': ''
        }

        # Check if position is valid
        if not self.tile_map.is_valid_position(target_x, target_y):
            result['message'] = "Invalid position"
            return result

        # For MVP, just allow placement
        # Later: check inventory for required materials
        success = self.tile_map.set_tile(target_x, target_y, tile_type_id)

        if success:
            result['success'] = True
            result['message'] = f"Placed {tile_type_id}"
        else:
            result['message'] = "Failed to place tile"

        return result

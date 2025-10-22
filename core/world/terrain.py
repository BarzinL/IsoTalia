"""
Terrain and tile type definitions.
Framework-agnostic tile properties and behaviors.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TileType:
    """Defines properties of a tile type."""

    id: str
    name: str
    walkable: bool
    hardness: int  # 0 = unbreakable, higher = harder to dig
    texture_id: str
    drops: List[str]  # Resource IDs that drop when harvested
    elevation_modifier: int = 0  # For rendering height

    def __hash__(self):
        return hash(self.id)


class TerrainRegistry:
    """Central registry for all tile types in the game."""

    def __init__(self):
        self._tiles = {}
        self._register_default_tiles()

    def register(self, tile_type: TileType):
        """Register a new tile type."""
        self._tiles[tile_type.id] = tile_type

    def get(self, tile_id: str) -> Optional[TileType]:
        """Get a tile type by ID."""
        return self._tiles.get(tile_id)

    def _register_default_tiles(self):
        """Register default tile types for MVP."""

        # Void/empty tile
        self.register(TileType(
            id="void",
            name="Void",
            walkable=False,
            hardness=0,
            texture_id="void",
            drops=[]
        ))

        # Basic wasteland ground
        self.register(TileType(
            id="wasteland_dirt",
            name="Wasteland Dirt",
            walkable=True,
            hardness=2,
            texture_id="wasteland_dirt",
            drops=["dirt", "small_rocks"]
        ))

        # Cracked pavement
        self.register(TileType(
            id="cracked_pavement",
            name="Cracked Pavement",
            walkable=True,
            hardness=4,
            texture_id="cracked_pavement",
            drops=["concrete_chunk", "rebar"]
        ))

        # Rubble pile (obstacle)
        self.register(TileType(
            id="rubble",
            name="Rubble",
            walkable=False,
            hardness=3,
            texture_id="rubble",
            drops=["scrap_metal", "concrete_chunk", "brick"]
        ))

        # Water/toxic waste
        self.register(TileType(
            id="toxic_water",
            name="Toxic Water",
            walkable=False,
            hardness=0,
            texture_id="toxic_water",
            drops=[]
        ))


# Global terrain registry instance
TERRAIN_REGISTRY = TerrainRegistry()

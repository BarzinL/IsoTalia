"""
TileMap - Core grid-based world representation.
Framework-agnostic, handles all tile operations.
"""

from typing import Optional, List, Tuple, Dict
from .terrain import TileType, TERRAIN_REGISTRY


class Tile:
    """Represents a single tile instance in the world."""

    def __init__(self, tile_type: TileType, z_level: int = 0):
        self.tile_type = tile_type
        self.z_level = z_level  # Elevation
        self.metadata = {}  # For custom properties (damage, growth, etc.)

    @property
    def walkable(self) -> bool:
        return self.tile_type.walkable

    @property
    def hardness(self) -> int:
        return self.tile_type.hardness


class TileMap:
    """
    Grid-based world representation.
    Coordinates: (x, y, z) where z is elevation.
    """

    def __init__(self, width: int, height: int, default_tile_id: str = "void"):
        self.width = width
        self.height = height
        self.default_tile_type = TERRAIN_REGISTRY.get(default_tile_id)

        # Main tile grid [x][y] = Tile
        self._tiles: Dict[Tuple[int, int], Tile] = {}

        # Initialize with default tiles
        self._initialize_map()

    def _initialize_map(self):
        """Fill map with default tiles."""
        for x in range(self.width):
            for y in range(self.height):
                self._tiles[(x, y)] = Tile(self.default_tile_type, z_level=0)

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within map bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position."""
        if not self.is_valid_position(x, y):
            return None
        return self._tiles.get((x, y))

    def set_tile(self, x: int, y: int, tile_type_id: str, z_level: int = 0):
        """Set tile at position."""
        if not self.is_valid_position(x, y):
            return False

        tile_type = TERRAIN_REGISTRY.get(tile_type_id)
        if tile_type is None:
            return False

        self._tiles[(x, y)] = Tile(tile_type, z_level)
        return True

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is walkable."""
        tile = self.get_tile(x, y)
        return tile is not None and tile.walkable

    def dig_tile(self, x: int, y: int) -> List[str]:
        """
        Dig/harvest a tile, returning dropped resources.
        Returns empty list if tile cannot be dug.
        """
        tile = self.get_tile(x, y)
        if tile is None or tile.hardness == 0:
            return []

        drops = tile.tile_type.drops.copy()

        # Replace with void or lower the z-level
        # For now, just replace with wasteland_dirt
        self.set_tile(x, y, "wasteland_dirt", tile.z_level)

        return drops

    def get_render_list(self, camera_x: int, camera_y: int,
                       view_width: int, view_height: int) -> List[dict]:
        """
        Get list of tiles to render for a given viewport.
        Returns list of dicts with tile data for rendering.
        """
        render_list = []

        # The camera_x and camera_y now represent the top-left corner of the viewport
        # view_width and view_height represent the dimensions of the viewport
        
        start_x = max(0, camera_x)
        end_x = min(self.width, camera_x + view_width)
        start_y = max(0, camera_y)
        end_y = min(self.height, camera_y + view_height)

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile = self.get_tile(x, y)
                if tile:
                    render_list.append({
                        'x': x,
                        'y': y,
                        'z': tile.z_level,
                        'texture_id': tile.tile_type.texture_id,
                        'tile_type': tile.tile_type.id
                    })

        return render_list

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring tile coordinates (4-directional)."""
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))

        return neighbors

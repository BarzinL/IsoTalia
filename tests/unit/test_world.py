"""Unit tests for the world and terrain systems."""
import pytest
from unittest.mock import Mock

from core.world.terrain import TileType, TerrainRegistry, TERRAIN_REGISTRY
from core.world.tile_map import Tile, TileMap


class TestTileType:
    """Test the TileType dataclass."""
    
    def test_tile_type_creation(self):
        """Test that TileTypes can be created."""
        tile_type = TileType(
            id="test_tile",
            name="Test Tile",
            walkable=True,
            hardness=2,
            texture_id="test_texture",
            drops=["test_drop"]
        )
        
        assert tile_type.id == "test_tile"
        assert tile_type.name == "Test Tile"
        assert tile_type.walkable is True
        assert tile_type.hardness == 2
        assert tile_type.texture_id == "test_texture"
        assert tile_type.drops == ["test_drop"]
    
    def test_tile_type_default_elevation_modifier(self):
        """Test that elevation_modifier defaults to 0."""
        tile_type = TileType(
            id="test_tile",
            name="Test Tile",
            walkable=True,
            hardness=2,
            texture_id="test_texture",
            drops=[]
        )
        
        assert tile_type.elevation_modifier == 0
    
    def test_tile_type_elevation_modifier(self):
        """Test that elevation_modifier can be set."""
        tile_type = TileType(
            id="test_tile",
            name="Test Tile",
            walkable=True,
            hardness=2,
            texture_id="test_texture",
            drops=[],
            elevation_modifier=5
        )
        
        assert tile_type.elevation_modifier == 5
    
    def test_tile_type_hash(self):
        """Test that TileTypes can be hashed."""
        tile_type = TileType(
            id="test_tile",
            name="Test Tile",
            walkable=True,
            hardness=2,
            texture_id="test_texture",
            drops=[]
        )
        
        # Should be hashable for use in sets/dicts
        tile_set = {tile_type}
        assert tile_type in tile_set


class TestTerrainRegistry:
    """Test the TerrainRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh terrain registry for testing."""
        return TerrainRegistry()
    
    def test_registry_creation(self):
        """Test that TerrainRegistry can be created."""
        registry = TerrainRegistry()
        
        assert isinstance(registry._tiles, dict)
        # Should have default tiles
        assert len(registry._tiles) > 0
    
    def test_register_tile_type(self, registry):
        """Test that tile types can be registered."""
        test_tile = TileType(
            id="custom_tile",
            name="Custom Tile",
            walkable=False,
            hardness=5,
            texture_id="custom_texture",
            drops=[]
        )
        
        registry.register(test_tile)
        
        assert "custom_tile" in registry._tiles
        assert registry._tiles["custom_tile"] == test_tile
    
    def test_get_existing_tile_type(self, registry):
        """Test getting an existing tile type."""
        # Should get one of the default tiles
        wasteland_dirt = registry.get("wasteland_dirt")
        
        assert wasteland_dirt is not None
        assert wasteland_dirt.id == "wasteland_dirt"
        assert wasteland_dirt.name == "Wasteland Dirt"
    
    def test_get_nonexistent_tile_type(self, registry):
        """Test getting a non-existent tile type."""
        result = registry.get("nonexistent_tile")
        
        assert result is None
    
    def test_global_registry_has_default_tiles(self):
        """Test that the global TERRAIN_REGISTRY has default tiles."""
        assert "wasteland_dirt" in TERRAIN_REGISTRY._tiles
        assert "rubble" in TERRAIN_REGISTRY._tiles
        assert "toxic_water" in TERRAIN_REGISTRY._tiles
        
        wasteland_dirt = TERRAIN_REGISTRY.get("wasteland_dirt")
        assert wasteland_dirt is not None
        assert wasteland_dirt.walkable is True
        assert wasteland_dirt.hardness == 2


class TestTile:
    """Test the Tile class."""
    
    def test_tile_creation(self):
        """Test that Tiles can be created."""
        tile_type = TileType(
            id="test_tile",
            name="Test Tile",
            walkable=True,
            hardness=2,
            texture_id="test_texture",
            drops=["test_drop"]
        )
        
        tile = Tile(tile_type, z_level=3)
        
        assert tile.tile_type == tile_type
        assert tile.z_level == 3
        assert tile.metadata == {}
    
    def test_tile_default_z_level(self):
        """Test that Tile defaults to z_level=0."""
        tile_type = TileType(
            id="test_tile",
            name="Test Tile",
            walkable=True,
            hardness=2,
            texture_id="test_texture",
            drops=[]
        )
        
        tile = Tile(tile_type)
        
        assert tile.z_level == 0
    
    def test_tile_walkable_property(self):
        """Test that Tile.walkable property works correctly."""
        walkable_type = TileType(
            id="walkable",
            name="Walkable",
            walkable=True,
            hardness=1,
            texture_id="test",
            drops=[]
        )
        
        unwalkable_type = TileType(
            id="unwalkable",
            name="Unwalkable",
            walkable=False,
            hardness=5,
            texture_id="test",
            drops=[]
        )
        
        walkable_tile = Tile(walkable_type)
        unwalkable_tile = Tile(unwalkable_type)
        
        assert walkable_tile.walkable is True
        assert unwalkable_tile.walkable is False
    
    def test_tile_hardness_property(self):
        """Test that Tile.hardness property works correctly."""
        soft_type = TileType(
            id="soft",
            name="Soft",
            walkable=True,
            hardness=1,
            texture_id="test",
            drops=[]
        )
        
        hard_type = TileType(
            id="hard",
            name="Hard",
            walkable=False,
            hardness=10,
            texture_id="test",
            drops=[]
        )
        
        soft_tile = Tile(soft_type)
        hard_tile = Tile(hard_type)
        
        assert soft_tile.hardness == 1
        assert hard_tile.hardness == 10


class TestTileMap:
    """Test the TileMap class."""
    
    @pytest.fixture
    def tile_map(self):
        """Create a fresh tile map for testing."""
        return TileMap(width=10, height=10, default_tile_id="wasteland_dirt")
    
    def test_tile_map_creation(self, tile_map):
        """Test that TileMaps can be created."""
        assert tile_map.width == 10
        assert tile_map.height == 10
        assert tile_map.default_tile_type is not None
        assert tile_map.default_tile_type.id == "wasteland_dirt"
    
    def test_tile_map_initialization(self, tile_map):
        """Test that TileMaps initialize with default tiles."""
        # Should have tiles for the entire map
        for x in range(10):
            for y in range(10):
                tile = tile_map.get_tile(x, y)
                assert tile is not None
                assert tile.tile_type.id == "wasteland_dirt"
    
    def test_is_valid_position(self, tile_map):
        """Test position validation."""
        assert tile_map.is_valid_position(0, 0) is True
        assert tile_map.is_valid_position(5, 5) is True
        assert tile_map.is_valid_position(9, 9) is True
        
        # Out of bounds
        assert tile_map.is_valid_position(-1, 5) is False
        assert tile_map.is_valid_position(5, -1) is False
        assert tile_map.is_valid_position(10, 5) is False
        assert tile_map.is_valid_position(5, 10) is False
    
    def test_get_tile(self, tile_map):
        """Test getting tiles."""
        tile = tile_map.get_tile(5, 5)
        
        assert tile is not None
        assert tile.tile_type.id == "wasteland_dirt"
        assert tile.z_level == 0
    
    def test_get_tile_out_of_bounds(self, tile_map):
        """Test getting tiles out of bounds."""
        tile = tile_map.get_tile(15, 15)
        
        assert tile is None
    
    def test_set_tile(self, tile_map):
        """Test setting tiles."""
        result = tile_map.set_tile(5, 5, "rubble")
        
        assert result is True
        
        tile = tile_map.get_tile(5, 5)
        assert tile is not None
        assert tile.tile_type.id == "rubble"
    
    def test_set_tile_out_of_bounds(self, tile_map):
        """Test setting tiles out of bounds."""
        result = tile_map.set_tile(15, 15, "rubble")
        
        assert result is False
    
    def test_set_tile_invalid_type(self, tile_map):
        """Test setting tiles with invalid type ID."""
        result = tile_map.set_tile(5, 5, "nonexistent_tile")
        
        assert result is False
        
        # Tile should remain unchanged
        tile = tile_map.get_tile(5, 5)
        assert tile.tile_type.id == "wasteland_dirt"
    
    def test_is_walkable(self, tile_map):
        """Test walkability checking."""
        # wasteland_dirt is walkable
        assert tile_map.is_walkable(5, 5) is True
        
        # Set to rubble (not walkable)
        tile_map.set_tile(5, 5, "rubble")
        assert tile_map.is_walkable(5, 5) is False
        
        # Set to void (not walkable)
        tile_map.set_tile(5, 5, "void")
        assert tile_map.is_walkable(5, 5) is False
    
    def test_dig_tile_success(self, tile_map):
        """Test successful tile digging."""
        # Set to cracked_pavement (hardness=4, drops resources)
        tile_map.set_tile(5, 5, "cracked_pavement")
        
        drops = tile_map.dig_tile(5, 5)
        
        # Should return drops
        assert "concrete_chunk" in drops
        assert "rebar" in drops
        
        # Tile should be changed to wasteland_dirt
        tile = tile_map.get_tile(5, 5)
        assert tile.tile_type.id == "wasteland_dirt"
    
    def test_dig_tile_unbreakable(self, tile_map):
        """Test digging unbreakable tiles."""
        # void tiles have hardness=0 (unbreakable)
        tile_map.set_tile(5, 5, "void")
        
        drops = tile_map.dig_tile(5, 5)
        
        # Should return empty list
        assert drops == []
        
        # Tile should remain unchanged
        tile = tile_map.get_tile(5, 5)
        assert tile.tile_type.id == "void"
    
    def test_dig_tile_out_of_bounds(self, tile_map):
        """Test digging tiles out of bounds."""
        drops = tile_map.dig_tile(15, 15)
        
        assert drops == []
    
    def test_get_render_list(self, tile_map):
        """Test getting render lists."""
        # Add some variety to the map
        tile_map.set_tile(5, 5, "rubble")
        tile_map.set_tile(6, 6, "toxic_water")
        
        render_list = tile_map.get_render_list(0, 0, 10, 10)
        
        assert len(render_list) == 100  # 10x10 grid
        
        # Check that our specific tiles are in the list
        rubble_found = False
        water_found = False
        
        for tile_data in render_list:
            if tile_data['x'] == 5 and tile_data['y'] == 5:
                assert tile_data['tile_type'] == 'rubble'
                rubble_found = True
            if tile_data['x'] == 6 and tile_data['y'] == 6:
                assert tile_data['tile_type'] == 'toxic_water'
                water_found = True
        
        assert rubble_found
        assert water_found
    
    def test_get_neighbors(self, tile_map):
        """Test getting neighboring tiles."""
        neighbors = tile_map.get_neighbors(5, 5)
        
        expected = [(5, 4), (6, 5), (5, 6), (4, 5)]  # N, E, S, W
        
        assert len(neighbors) == 4
        assert all(neighbor in neighbors for neighbor in expected)
    
    def test_get_neighbors_edge_of_map(self, tile_map):
        """Test getting neighbors at the edge of the map."""
        # Top-left corner - fewer neighbors
        neighbors = tile_map.get_neighbors(0, 0)
        expected = [(1, 0), (0, 1)]  # Only E, S
        
        assert len(neighbors) == 2
        assert all(neighbor in neighbors for neighbor in expected)
        
        # Top edge
        neighbors = tile_map.get_neighbors(5, 0)
        expected = [(5, 1), (6, 0), (4, 0)]  # S, E, W (no N)
        
        assert len(neighbors) == 3
        assert all(neighbor in neighbors for neighbor in expected)
    
    def test_get_neighbors_out_of_bounds(self, tile_map):
        """Test getting neighbors for out of bounds position."""
        # This shouldn't happen normally, but test robustness
        neighbors = tile_map.get_neighbors(-1, -1)
        
        # Should return valid neighbors only
        assert len(neighbors) == 0
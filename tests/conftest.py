"""Global pytest configuration and fixtures."""
import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_tile_types():
    """Provide sample tile types for testing."""
    from core.world.terrain import TileType
    
    return {
        "test_ground": TileType(
            id="test_ground",
            name="Test Ground",
            walkable=True,
            hardness=1,
            texture_id="test_ground",
            drops=["test_item"]
        ),
        "test_wall": TileType(
            id="test_wall",
            name="Test Wall",
            walkable=False,
            hardness=3,
            texture_id="test_wall",
            drops=["test_scrap"]
        ),
        "test_water": TileType(
            id="test_water",
            name="Test Water",
            walkable=False,
            hardness=0,
            texture_id="test_water",
            drops=[]
        )
    }

@pytest.fixture
def mock_game_state():
    """Provide a mock game state for testing."""
    from core import GameState
    
    game_state = GameState(map_width=20, map_height=20)
    game_state.initialize()
    return game_state

@pytest.fixture
def mock_player():
    """Provide a mock player entity for testing."""
    from core.entities.player import create_player
    
    return create_player(10, 10, 0)

@pytest.fixture
def mock_tile_map():
    """Provide a mock tile map for testing."""
    from core.world.tile_map import TileMap
    
    tile_map = TileMap(50, 50, "wasteland_dirt")
    return tile_map

@pytest.fixture
def mock_entity_manager():
    """Provide a mock entity manager for testing."""
    from core.entities.entity import EntityManager
    
    return EntityManager()

@pytest.fixture
def mock_event_bus():
    """Provide a mock event bus for testing."""
    from core.events import EventBus
    
    return EventBus()

# Mark slow tests to skip in quick runs
slow = pytest.mark.slow

# Mark tests that require pygame
pygame_required = pytest.mark.pygame

# Mark tests that are game-specific
game_specific = pytest.mark.game
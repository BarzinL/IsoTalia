"""Pytest configuration and shared fixtures."""
import pytest

from core.events import EventType, Event, EVENT_BUS
from core.entities.entity import Entity
from core.entities.components import Position, Renderable, Movement
from core.world.tile_map import TileMap
from core.world.terrain import TERRAIN_REGISTRY
from core.game_state import GameState


@pytest.fixture
def mock_event_bus():
    """Create a fresh event bus for testing."""
    from core.events import EventBus
    return EventBus()


@pytest.fixture
def mock_game_state():
    """Create a fresh game state for testing."""
    return GameState(map_width=10, map_height=10)


@pytest.fixture
def sample_entity():
    """Create a sample entity with components."""
    entity = Entity(entity_id=100)
    entity.add_component(Position(5, 5, 0))
    entity.add_component(Renderable("test_texture"))
    entity.add_component(Movement())
    return entity


@pytest.fixture
def sample_tile_map():
    """Create a sample tile map for testing."""
    return TileMap(10, 10, "wasteland_dirt")


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {"player_id": 1, "x": 5, "y": 10, "z": 0}


@pytest.fixture
def events_with_data(mock_event_bus, sample_event_data):
    """Create sample events for testing."""
    return Event(EventType.GAME_STARTED, sample_event_data)


@pytest.fixture
def entity_with_position():
    """Create an entity at a specific position."""
    entity = Entity(entity_id=200)
    entity.add_component(Position(3, 4, 0))
    return entity


@pytest.fixture
def tile_map_with_variety():
    """Create a tile map with various tile types."""
    tile_map = TileMap(10, 10, "wasteland_dirt")
    tile_map.set_tile(2, 2, "rubble")
    tile_map.set_tile(3, 3, "toxic_water")
    tile_map.set_tile(4, 4, "cracked_pavement")
    return tile_map


@pytest.fixture(autouse=True)
def clean_event_bus():
    """Clean the global event bus before and after each test."""
    EVENT_BUS.clear()
    yield
    EVENT_BUS.clear()


@pytest.fixture
def mock_player():
    """Create a mock player entity."""
    player = Entity(entity_id=999)
    player.add_component(Position(5, 5, 0))
    return player
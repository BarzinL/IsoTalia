"""
Core game state manager.
Framework-agnostic game logic orchestration.
"""

from typing import Optional
from .world.tile_map import TileMap
from .entities.entity import EntityManager
from .entities.player import create_player, PlayerController
from .systems.movement import MovementSystem
from .systems.interaction import InteractionSystem
from .events import EventBus, Event, EventType, EVENT_BUS
from .settings import DEFAULT_SETTINGS


class GameState:
    """
    Central game state that coordinates all systems.
    Framework-agnostic - contains no rendering code.
    """

    def __init__(self, map_width: int = 50, map_height: int = 50):
        # Core systems
        self.tile_map = TileMap(map_width, map_height, default_tile_id="wasteland_dirt")
        self.entity_manager = EntityManager()
        self.event_bus = EVENT_BUS

        # Game systems
        self.movement_system = MovementSystem(self.tile_map, self.entity_manager)
        self.interaction_system = InteractionSystem(self.tile_map)

        # Player
        self.player_entity = None
        self.player_controller = None

        # Game state
        self.is_running = False
        self.is_paused = False
        self.game_time = 0.0  # Total elapsed game time
        
        # Settings
        self.settings = DEFAULT_SETTINGS

    def initialize(self):
        """Initialize the game state."""
        # Create player at starting position
        self.player_entity = create_player(x=25, y=25, z=0)
        self.entity_manager.add_entity(self.player_entity)
        self.player_controller = PlayerController(self.player_entity)

        # Generate a simple test world
        self._generate_test_world()

        # Publish game started event
        self.event_bus.publish(Event(
            EventType.GAME_STARTED,
            {'timestamp': self.game_time}
        ))

        self.is_running = True

    def _generate_test_world(self):
        """Generate a simple test world for MVP."""
        # Create a small area with different tiles
        # Add some rubble obstacles
        for x in range(10, 15):
            self.tile_map.set_tile(x, 10, "rubble")

        # Add some cracked pavement
        for x in range(20, 30):
            for y in range(20, 25):
                self.tile_map.set_tile(x, y, "cracked_pavement")

        # Add a small toxic water pool
        for x in range(15, 18):
            for y in range(15, 18):
                self.tile_map.set_tile(x, y, "toxic_water")

    def update(self, delta_time: float):
        """
        Update game state.
        delta_time: time since last update in seconds.
        """
        if not self.is_running or self.is_paused:
            return

        self.game_time += delta_time

        # Update systems here
        # For MVP, most updates are event-driven, not time-based

    def process_command(self, command: str) -> bool:
        """
        Process a game command (from input system).
        Returns True if command was handled.
        """
        if not self.is_running or self.is_paused:
            return False

        # Movement commands
        if command.startswith('move_'):
            success = self.movement_system.process_movement_command(
                self.player_entity, command
            )
            if success:
                pos = self.player_controller.get_position()
                self.event_bus.publish(Event(
                    EventType.ENTITY_MOVED,
                    {'entity_id': self.player_entity.id, 'x': pos.x, 'y': pos.y}
                ))
            return success

        # Dig command
        if command == 'dig':
            # Dig in the direction the player is facing (for MVP, just dig north)
            result = self.interaction_system.dig_adjacent(self.player_entity, 'north')
            if result['success']:
                self.event_bus.publish(Event(
                    EventType.TILE_DIG,
                    result
                ))
            return result['success']

        return False
    
    def process_continuous_command(self, command: str, delta_time: float) -> bool:
        """
        Process a continuous movement command (for held keys).
        Returns True if command was handled.
        """
        if not self.is_running or self.is_paused:
            return False
            
        if not self.settings.enable_continuous_movement:
            return False
            
        # Only handle movement commands continuously
        if command.startswith('move_'):
            # Check if enough time has passed for another movement
            if self.player_controller.can_move_continuously(delta_time):
                success = self.movement_system.process_movement_command(
                    self.player_entity, command
                )
                if success:
                    pos = self.player_controller.get_position()
                    self.event_bus.publish(Event(
                        EventType.ENTITY_MOVED,
                        {'entity_id': self.player_entity.id, 'x': pos.x, 'y': pos.y}
                    ))
                return success
        return False

    def get_render_data(self, camera_x: int, camera_y: int,
                       view_width: int, view_height: int) -> dict:
        """
        Get all data needed for rendering.
        Returns framework-agnostic render data.
        """
        # Get visible tiles
        tiles = self.tile_map.get_render_list(camera_x, camera_y, view_width, view_height)

        # Get all entities with position and renderable components
        entities = []
        for entity in self.entity_manager.get_all_entities():
            from .entities.components import Position, Renderable
            pos = entity.get_component(Position)
            renderable = entity.get_component(Renderable)

            if pos and renderable:
                entities.append({
                    'id': entity.id,
                    'x': pos.x,
                    'y': pos.y,
                    'z': pos.z,
                    'texture_id': renderable.texture_id,
                    'layer': renderable.layer,
                    'offset_x': renderable.offset_x,
                    'offset_y': renderable.offset_y,
                })

        return {
            'tiles': tiles,
            'entities': entities,
            'camera': {'x': camera_x, 'y': camera_y},
            'game_time': self.game_time
        }

    def pause(self):
        """Pause the game."""
        self.is_paused = True
        self.event_bus.publish(Event(EventType.GAME_PAUSED, {}))

    def resume(self):
        """Resume the game."""
        self.is_paused = False
        self.event_bus.publish(Event(EventType.GAME_RESUMED, {}))

    def shutdown(self):
        """Clean shutdown of game state."""
        self.is_running = False
        self.entity_manager.clear()

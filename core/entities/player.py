"""
Player entity creation and player-specific logic.
"""

from .entity import Entity
from .components import Position, Renderable, Movement, Inventory, Health, Tool
from ..settings import DEFAULT_SETTINGS


def create_player(x: int, y: int, z: int = 0) -> Entity:
    """
    Factory function to create a player entity with all necessary components.
    """
    player = Entity()

    # Position
    player.add_component(Position(x=x, y=y, z=z))

    # Visual representation
    player.add_component(Renderable(
        texture_id="player",
        layer=1
    ))

    # Movement capabilities
    player.add_component(Movement(
        speed=1.0,
        can_fly=False,
        can_swim=False
    ))

    # Inventory
    player.add_component(Inventory(capacity=20))

    # Health
    player.add_component(Health(maximum=100))

    # Starting tool - basic shovel
    player.add_component(Tool(
        tool_type="shovel",
        power=2,
        durability=100,
        max_durability=100
    ))

    return player


class PlayerController:
    """
    Player-specific game logic.
    Handles player actions and interactions.
    """

    def __init__(self, player_entity: Entity):
        self.player = player_entity
        self.movement_timer = 0.0  # Time since last movement
        self.movement_frequency = DEFAULT_SETTINGS.movement_frequency

    def get_position(self) -> Position:
        """Get player's current position."""
        return self.player.get_component(Position)

    def move_to(self, x: int, y: int):
        """Move player to new position (used by movement system)."""
        pos = self.get_position()
        if pos:
            pos.x = x
            pos.y = y

    def get_inventory(self) -> Inventory:
        """Get player's inventory."""
        return self.player.get_component(Inventory)

    def get_tool(self) -> Tool:
        """Get player's current tool."""
        return self.player.get_component(Tool)

    def get_health(self) -> Health:
        """Get player's health."""
        return self.player.get_component(Health)

    def is_alive(self) -> bool:
        """Check if player is alive."""
        health = self.get_health()
        return health is not None and health.is_alive
    
    def can_move_continuously(self, delta_time: float) -> bool:
        """
        Check if player can move based on movement frequency timer.
        Returns True if enough time has passed for another movement.
        """
        self.movement_timer += delta_time
        movement_interval = 1.0 / self.movement_frequency
        
        if self.movement_timer >= movement_interval:
            self.movement_timer = 0.0
            return True
        return False
    
    def set_movement_frequency(self, frequency: float):
        """Set the movement frequency (movements per second)."""
        self.movement_frequency = max(0.1, frequency)  # Prevent division by zero

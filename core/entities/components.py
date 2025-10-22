"""
Component definitions for entity-component system.
Components are pure data containers.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    """Grid position component."""
    x: int
    y: int
    z: int = 0  # Z-level elevation

    def to_tuple(self) -> tuple:
        """Return as (x, y, z) tuple."""
        return (self.x, self.y, self.z)


@dataclass
class Renderable:
    """Visual representation component."""
    texture_id: str
    sprite_sheet: Optional[str] = None
    offset_x: int = 0  # Pixel offset for fine positioning
    offset_y: int = 0
    layer: int = 1  # Render layer (0=ground, 1=entities, 2=effects)


@dataclass
class Movement:
    """Movement capabilities component."""
    speed: float = 1.0  # Tiles per second
    can_fly: bool = False
    can_swim: bool = False


@dataclass
class Inventory:
    """Inventory component for carrying items."""
    capacity: int
    items: list

    def __init__(self, capacity: int = 20):
        self.capacity = capacity
        self.items = []

    def add_item(self, item_id: str) -> bool:
        """Add item to inventory if space available."""
        if len(self.items) < self.capacity:
            self.items.append(item_id)
            return True
        return False

    def remove_item(self, item_id: str) -> bool:
        """Remove item from inventory."""
        if item_id in self.items:
            self.items.remove(item_id)
            return True
        return False


@dataclass
class Tool:
    """Tool component for interacting with tiles."""
    tool_type: str  # "pickaxe", "shovel", "axe", etc.
    power: int = 1  # Mining/digging power
    durability: int = 100
    max_durability: int = 100

    def use(self) -> bool:
        """Use the tool, reducing durability. Returns False if broken."""
        self.durability = max(0, self.durability - 1)
        return self.durability > 0


@dataclass
class Health:
    """Health component."""
    current: int
    maximum: int

    def __init__(self, maximum: int = 100):
        self.maximum = maximum
        self.current = maximum

    @property
    def is_alive(self) -> bool:
        return self.current > 0

    def damage(self, amount: int):
        """Take damage."""
        self.current = max(0, self.current - amount)

    def heal(self, amount: int):
        """Restore health."""
        self.current = min(self.maximum, self.current + amount)

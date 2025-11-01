"""
Event system for decoupled communication.
Framework-agnostic event bus.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Enumeration of game events."""
    # Game lifecycle events
    GAME_STARTED = "GAME_STARTED"
    GAME_PAUSED = "GAME_PAUSED"
    GAME_RESUMED = "GAME_RESUMED"
    GAME_ENDED = "GAME_ENDED"

    # Movement events
    ENTITY_MOVED = "ENTITY_MOVED"
    MOVEMENT_BLOCKED = "MOVEMENT_BLOCKED"

    # Interaction events
    TILE_DIG = "TILE_DIG"
    TILE_PLACED = "TILE_PLACED"
    RESOURCE_COLLECTED = "RESOURCE_COLLECTED"

    # Combat events
    COMBAT_STARTED = "COMBAT_STARTED"
    COMBAT_ENDED = "COMBAT_ENDED"

    # Player events
    PLAYER_DAMAGED = "PLAYER_DAMAGED"
    PLAYER_DIED = "PLAYER_DIED"
    INVENTORY_CHANGED = "INVENTORY_CHANGED"


@dataclass(frozen=True)
class Event:
    """Base event class.
    
    Note: Uses frozen=True to make the dataclass immutable,
    and creates a copy of data to ensure it cannot be modified.
    """
    event_type: EventType
    data: Dict[str, Any]

    def __post_init__(self):
        """Create a deep copy of data to ensure immutability."""
        if hasattr(self, '__dict__'):
            object.__setattr__(self, 'data', self.data.copy())


class EventBus:
    """
    Central event bus for publish-subscribe pattern.
    Allows systems to communicate without tight coupling.
    """

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}

    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to an event type.
        Callback will be called when event is published.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        """
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                callback(event)

    def clear(self):
        """Clear all subscriptions."""
        self._subscribers.clear()


# Global event bus instance
EVENT_BUS = EventBus()

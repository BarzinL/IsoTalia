"""
Event system for decoupled communication.
Framework-agnostic event bus.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum, auto


class EventType(Enum):
    """Enumeration of game events."""
    # Movement events
    ENTITY_MOVED = auto()
    MOVEMENT_BLOCKED = auto()

    # Interaction events
    TILE_DIG = auto()
    TILE_PLACED = auto()
    RESOURCE_COLLECTED = auto()

    # Player events
    PLAYER_DAMAGED = auto()
    PLAYER_DIED = auto()
    INVENTORY_CHANGED = auto()

    # System events
    GAME_STARTED = auto()
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()


@dataclass
class Event:
    """Base event class."""
    event_type: EventType
    data: Dict[str, Any]


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

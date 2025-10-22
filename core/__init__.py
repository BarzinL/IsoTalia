"""
IsoTalia Core Engine
Framework-agnostic game logic.
"""

from .game_state import GameState
from .events import EventBus, Event, EventType, EVENT_BUS

__all__ = ['GameState', 'EventBus', 'Event', 'EventType', 'EVENT_BUS']

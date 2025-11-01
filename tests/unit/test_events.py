"""Unit tests for the event system."""
import pytest
from unittest.mock import Mock

from core.events import EventBus, Event, EventType, EVENT_BUS


class TestEvent:
    """Test the Event dataclass."""
    
    def test_event_creation(self):
        """Test that events can be created with type and data."""
        event_type = EventType.GAME_STARTED
        data = {"test_key": "test_value"}
        
        event = Event(event_type, data)
        
        assert event.event_type == event_type
        assert event.data == data
    
    def test_event_data_immutable(self):
        """Test that event data cannot be modified after creation."""
        data = {"test_key": "test_value"}
        event = Event(EventType.GAME_STARTED, data)
        
        # Attempting to modify data should not affect the event
        data["test_key"] = "modified_value"
        
        assert event.data["test_key"] == "test_value"


class TestEventBus:
    """Test the EventBus class."""
    
    @pytest.fixture
    def event_bus(self):
        """Create a fresh event bus for testing."""
        return EventBus()
    
    def test_subscribe_unsubscribe(self, event_bus):
        """Test that subscriptions can be added and removed."""
        callback = Mock()
        
        # Subscribe to event
        event_bus.subscribe(EventType.GAME_STARTED, callback)
        assert EventType.GAME_STARTED in event_bus._subscribers
        assert callback in event_bus._subscribers[EventType.GAME_STARTED]
        
        # Unsubscribe
        event_bus.unsubscribe(EventType.GAME_STARTED, callback)
        assert callback not in event_bus._subscribers[EventType.GAME_STARTED]
    
    def test_publish_event(self, event_bus):
        """Test that events are published to subscribers."""
        callback = Mock()
        event_bus.subscribe(EventType.GAME_STARTED, callback)
        
        test_event = Event(EventType.GAME_STARTED, {"test": "data"})
        event_bus.publish(test_event)
        
        callback.assert_called_once_with(test_event)
    
    def test_multiple_subscribers(self, event_bus):
        """Test that multiple subscribers receive the same event."""
        callback1 = Mock()
        callback2 = Mock()
        
        event_bus.subscribe(EventType.GAME_STARTED, callback1)
        event_bus.subscribe(EventType.GAME_STARTED, callback2)
        
        test_event = Event(EventType.GAME_STARTED, {"test": "data"})
        event_bus.publish(test_event)
        
        callback1.assert_called_once_with(test_event)
        callback2.assert_called_once_with(test_event)
    
    def test_unsubscribe_nonexistent_callback(self, event_bus):
        """Test that unsubscribing a non-existent callback doesn't raise an error."""
        callback = Mock()
        
        # Should not raise an error
        event_bus.unsubscribe(EventType.GAME_STARTED, callback)
    
    def test_publish_to_nonexistent_event_type(self, event_bus):
        """Test that publishing to an event type with no subscribers doesn't raise an error."""
        test_event = Event(EventType.GAME_STARTED, {"test": "data"})
        
        # Should not raise an error even though no one is subscribed
        event_bus.publish(test_event)


class TestGlobalEventBus:
    """Test the global EVENT_BUS instance."""
    
    def test_global_event_bus_exists(self):
        """Test that the global EVENT_BUS is properly initialized."""
        assert EVENT_BUS is not None
        assert isinstance(EVENT_BUS, EventBus)
    
    def test_global_event_bus_publish(self):
        """Test that the global event bus can publish events."""
        callback = Mock()
        EVENT_BUS.subscribe(EventType.GAME_STARTED, callback)
        
        test_event = Event(EventType.GAME_STARTED, {"test": "global"})
        EVENT_BUS.publish(test_event)
        
        callback.assert_called_once_with(test_event)
        
        # Cleanup
        EVENT_BUS.unsubscribe(EventType.GAME_STARTED, callback)


class TestEventTypes:
    """Test that all event types are properly defined."""
    
    def test_event_types_exist(self):
        """Test that all expected event types exist."""
        expected_types = [
            "GAME_STARTED",
            "GAME_PAUSED",
            "GAME_RESUMED",
            "GAME_ENDED",
            "ENTITY_MOVED",
            "TILE_DIG",
            "COMBAT_STARTED",
            "COMBAT_ENDED",
            "INVENTORY_CHANGED"
        ]
        
        for event_type_name in expected_types:
            assert hasattr(EventType, event_type_name)
    
    def test_event_types_are_enum_values(self):
        """Test that event types are proper enum values."""
        for event_type in EventType:
            assert isinstance(event_type, EventType)
            assert isinstance(event_type.value, str)
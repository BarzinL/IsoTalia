"""Unit tests for the entity and component systems."""
import pytest
from unittest.mock import Mock

from core.entities.entity import Entity, EntityManager
from core.entities.components import (
    Position, Renderable, Movement, Inventory, Tool, Health
)


class TestEntity:
    """Test the Entity class."""
    
    def test_entity_creation(self):
        """Test that entities can be created."""
        entity = Entity()
        
        assert entity.id is not None
        assert isinstance(entity.id, int)
        assert len(entity._components) == 0
    
    def test_entity_creation_with_id(self):
        """Test that entities can be created with a specific ID."""
        entity = Entity(entity_id=42)
        
        assert entity.id == 42
    
    def test_add_component(self):
        """Test that components can be added to entities."""
        entity = Entity()
        position = Position(5, 10, 0)
        
        entity.add_component(position)
        
        assert entity.has_component(Position)
        assert entity.get_component(Position) == position
    
    def test_get_component(self):
        """Test that components can be retrieved from entities."""
        entity = Entity()
        position = Position(5, 10, 0)
        renderable = Renderable("test_texture")
        
        entity.add_component(position)
        entity.add_component(renderable)
        
        assert entity.get_component(Position) == position
        assert entity.get_component(Renderable) == renderable
        assert entity.get_component(Movement) is None
    
    def test_has_component(self):
        """Test that components can be checked for existence."""
        entity = Entity()
        position = Position(5, 10, 0)
        
        assert not entity.has_component(Position)
        
        entity.add_component(position)
        assert entity.has_component(Position)
    
    def test_remove_component(self):
        """Test that components can be removed from entities."""
        entity = Entity()
        position = Position(5, 10, 0)
        
        entity.add_component(position)
        assert entity.has_component(Position)
        
        entity.remove_component(Position)
        assert not entity.has_component(Position)
        assert entity.get_component(Position) is None
    
    def test_to_dict(self):
        """Test that entities can be serialized to dictionaries."""
        entity = Entity(entity_id=123)
        position = Position(5, 10, 0)
        renderable = Renderable("test_texture", layer=2)
        
        entity.add_component(position)
        entity.add_component(renderable)
        
        result = entity.to_dict()
        
        assert result["id"] == 123
        assert "components" in result
        assert "Position" in result["components"]
        assert "Renderable" in result["components"]
        assert result["components"]["Position"]["x"] == 5
        assert result["components"]["Position"]["y"] == 10
        assert result["components"]["Position"]["z"] == 0


class TestEntityManager:
    """Test the EntityManager class."""
    
    @pytest.fixture
    def entity_manager(self):
        """Create a fresh entity manager for testing."""
        return EntityManager()
    
    def test_create_entity(self, entity_manager):
        """Test that entities can be created through the manager."""
        entity = entity_manager.create_entity()
        
        assert entity is not None
        assert isinstance(entity, Entity)
        assert entity.id in entity_manager._entities
        assert entity_manager.get_entity(entity.id) == entity
    
    def test_add_entity(self, entity_manager):
        """Test that entities can be added to the manager."""
        entity = Entity(entity_id=999)
        
        entity_manager.add_entity(entity)
        
        assert entity_manager.get_entity(999) == entity
        assert entity in entity_manager.get_all_entities()
    
    def test_remove_entity(self, entity_manager):
        """Test that entities can be removed from the manager."""
        entity = entity_manager.create_entity()
        entity_id = entity.id
        
        entity_manager.remove_entity(entity_id)
        
        assert entity_manager.get_entity(entity_id) is None
        assert entity not in entity_manager.get_all_entities()
    
    def test_remove_nonexistent_entity(self, entity_manager):
        """Test that removing a non-existent entity doesn't raise an error."""
        entity_manager.remove_entity(999)  # Should not raise
    
    def test_get_all_entities(self, entity_manager):
        """Test that all entities can be retrieved."""
        entity1 = entity_manager.create_entity()
        entity2 = entity_manager.create_entity()
        entity3 = Entity(entity_id=777)
        entity_manager.add_entity(entity3)
        
        all_entities = entity_manager.get_all_entities()
        
        assert len(all_entities) == 3
        assert entity1 in all_entities
        assert entity2 in all_entities
        assert entity3 in all_entities
    
    def test_get_entities_with_component(self, entity_manager):
        """Test that entities can be queried by component type."""
        entity1 = entity_manager.create_entity()
        entity1.add_component(Position(1, 1, 0))
        
        entity2 = entity_manager.create_entity()
        entity2.add_component(Position(2, 2, 0))
        
        entity3 = entity_manager.create_entity()
        entity3.add_component(Renderable("test"))
        # No Position component
        
        entities_with_position = entity_manager.get_entities_with_component(Position)
        
        assert len(entities_with_position) == 2
        assert entity1 in entities_with_position
        assert entity2 in entities_with_position
        assert entity3 not in entities_with_position
    
    def test_get_entities_at_position(self, entity_manager):
        """Test that entities can be queried by position."""
        entity1 = entity_manager.create_entity()
        entity1.add_component(Position(5, 5, 0))
        
        entity2 = entity_manager.create_entity()
        entity2.add_component(Position(5, 5, 0))  # Same position
        
        entity3 = entity_manager.create_entity()
        entity3.add_component(Position(10, 10, 0))
        
        entities_at_5_5 = entity_manager.get_entities_at_position(5, 5)
        
        assert len(entities_at_5_5) == 2
        assert entity1 in entities_at_5_5
        assert entity2 in entities_at_5_5
        assert entity3 not in entities_at_5_5
        
        entities_at_10_10 = entity_manager.get_entities_at_position(10, 10)
        assert len(entities_at_10_10) == 1
        assert entity3 in entities_at_10_10
    
    def test_clear(self, entity_manager):
        """Test that all entities can be cleared from the manager."""
        entity_manager.create_entity()
        entity_manager.create_entity()
        entity_manager.create_entity()
        
        assert len(entity_manager.get_all_entities()) == 3
        
        entity_manager.clear()
        
        assert len(entity_manager.get_all_entities()) == 0


class TestPositionComponent:
    """Test the Position component."""
    
    def test_position_creation(self):
        """Test that Position components can be created."""
        position = Position(10, 20, 5)
        
        assert position.x == 10
        assert position.y == 20
        assert position.z == 5
    
    def test_position_default_z(self):
        """Test that Position components default to z=0."""
        position = Position(10, 20)
        
        assert position.x == 10
        assert position.y == 20
        assert position.z == 0
    
    def test_position_to_tuple(self):
        """Test that Position can be converted to tuple."""
        position = Position(10, 20, 5)
        result = position.to_tuple()
        
        assert result == (10, 20, 5)


class TestInventoryComponent:
    """Test the Inventory component."""
    
    def test_inventory_creation(self):
        """Test that Inventory components can be created."""
        inventory = Inventory(capacity=10)
        
        assert inventory.capacity == 10
        assert inventory.items == []
    
    def test_inventory_add_item(self):
        """Test that items can be added to inventory."""
        inventory = Inventory(capacity=5)
        
        result = inventory.add_item("test_item")
        
        assert result is True
        assert "test_item" in inventory.items
    
    def test_inventory_add_item_full(self):
        """Test that items cannot be added when inventory is full."""
        inventory = Inventory(capacity=2)
        inventory.add_item("item1")
        inventory.add_item("item2")
        
        result = inventory.add_item("item3")
        
        assert result is False
        assert len(inventory.items) == 2
        assert "item3" not in inventory.items
    
    def test_inventory_remove_item(self):
        """Test that items can be removed from inventory."""
        inventory = Inventory(capacity=5)
        inventory.add_item("test_item")
        inventory.add_item("another_item")
        
        result = inventory.remove_item("test_item")
        
        assert result is True
        assert "test_item" not in inventory.items
        assert "another_item" in inventory.items
    
    def test_inventory_remove_nonexistent_item(self):
        """Test that removing a non-existent item returns False."""
        inventory = Inventory(capacity=5)
        inventory.add_item("existing_item")
        
        result = inventory.remove_item("nonexistent_item")
        
        assert result is False


class TestToolComponent:
    """Test the Tool component."""
    
    def test_tool_creation(self):
        """Test that Tool components can be created."""
        tool = Tool(tool_type="pickaxe", power=5, durability=100)
        
        assert tool.tool_type == "pickaxe"
        assert tool.power == 5
        assert tool.durability == 100
        assert tool.max_durability == 100
    
    def test_tool_use(self):
        """Test that using a tool reduces durability."""
        tool = Tool(tool_type="pickaxe", durability=100, max_durability=100)
        
        result = tool.use()
        
        assert result is True  # Tool not broken
        assert tool.durability == 99
    
    def test_tool_use_until_broken(self):
        """Test that tools break when durability reaches zero."""
        tool = Tool(tool_type="pickaxe", durability=1, max_durability=100)
        
        # Use once
        result1 = tool.use()
        assert result1 is False  # Tool broken
        assert tool.durability == 0
        
        # Use again
        result2 = tool.use()
        assert result2 is False
        assert tool.durability == 0


class TestHealthComponent:
    """Test the Health component."""
    
    def test_health_creation(self):
        """Test that Health components can be created."""
        health = Health(maximum=100)
        
        assert health.current == 100
        assert health.maximum == 100
        assert health.is_alive is True
    
    def test_health_is_alive(self):
        """Test that is_alive property works correctly."""
        health_alive = Health(maximum=100)
        health_alive.current = 50
        assert health_alive.is_alive is True
        
        health_dead = Health(maximum=100)
        health_dead.current = 0
        assert health_dead.is_alive is False
    
    def test_health_damage(self):
        """Test that damage reduces health."""
        health = Health(maximum=100)
        health.damage(30)
        
        assert health.current == 70
        assert health.is_alive is True
        
        health.damage(80)
        assert health.current == 0
        assert health.is_alive is False
    
    def test_health_heal(self):
        """Test that healing restores health."""
        health = Health(maximum=100)
        health.current = 30
        health.heal(20)
        
        assert health.current == 50
        assert health.is_alive is True
        
        health.heal(100)
        assert health.current == 100  # Should not exceed maximum
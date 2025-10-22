"""
Base Entity class and entity management.
Simple component-based entity system.
"""

from typing import Optional, Any, Dict
from .components import Position, Renderable, Movement, Inventory, Health


class Entity:
    """
    Base entity class using composition.
    Entities are identified by unique IDs and contain components.
    """

    _next_id = 0

    def __init__(self, entity_id: Optional[int] = None):
        if entity_id is None:
            self.id = Entity._next_id
            Entity._next_id += 1
        else:
            self.id = entity_id

        # Component storage
        self._components: Dict[type, Any] = {}

    def add_component(self, component: Any):
        """Add a component to this entity."""
        self._components[type(component)] = component

    def get_component(self, component_type: type) -> Optional[Any]:
        """Get a component by type."""
        return self._components.get(component_type)

    def has_component(self, component_type: type) -> bool:
        """Check if entity has a component."""
        return component_type in self._components

    def remove_component(self, component_type: type):
        """Remove a component from entity."""
        if component_type in self._components:
            del self._components[component_type]

    def to_dict(self) -> dict:
        """Serialize entity to dict for rendering/networking."""
        data = {'id': self.id, 'components': {}}

        for comp_type, component in self._components.items():
            comp_name = comp_type.__name__
            if hasattr(component, '__dict__'):
                data['components'][comp_name] = component.__dict__
            else:
                data['components'][comp_name] = str(component)

        return data


class EntityManager:
    """
    Manages all entities in the game.
    Provides queries and lifecycle management.
    """

    def __init__(self):
        self._entities: Dict[int, Entity] = {}

    def create_entity(self) -> Entity:
        """Create a new entity and register it."""
        entity = Entity()
        self._entities[entity.id] = entity
        return entity

    def add_entity(self, entity: Entity):
        """Add an existing entity to the manager."""
        self._entities[entity.id] = entity

    def remove_entity(self, entity_id: int):
        """Remove an entity from the manager."""
        if entity_id in self._entities:
            del self._entities[entity_id]

    def get_entity(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID."""
        return self._entities.get(entity_id)

    def get_all_entities(self) -> list:
        """Get all entities."""
        return list(self._entities.values())

    def get_entities_with_component(self, component_type: type) -> list:
        """Get all entities that have a specific component."""
        return [
            entity for entity in self._entities.values()
            if entity.has_component(component_type)
        ]

    def get_entities_at_position(self, x: int, y: int) -> list:
        """Get all entities at a specific grid position."""
        entities = []
        for entity in self.get_entities_with_component(Position):
            pos = entity.get_component(Position)
            if pos and pos.x == x and pos.y == y:
                entities.append(entity)
        return entities

    def clear(self):
        """Remove all entities."""
        self._entities.clear()

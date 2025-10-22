# IsoTalia Meta-Architecture

## Design Philosophy

**Core Principle:** Maximum abstraction for portability across single-player, MMORPG, isometric, and 3D implementations.

All game logic is **mode-agnostic**, **input-agnostic**, and **rendering-agnostic**.

---

## Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER (Framework-Specific)                │
│  - Input Adapters: Keyboard, Mouse, Touch, Network     │
│  - Rendering: PyGame, Unity, Godot, Three.js           │
│  - Audio, UI, Effects                                   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  COMMAND LAYER (Framework-Agnostic)                     │
│  - Input → Command translation                          │
│  - Command validation                                   │
│  - Command queuing (for pathfinding, AI)               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  ACTION LAYER (Pure Game Logic)                         │
│  - Everything is an Action with AP cost                 │
│  - Action execution (move, attack, use item)            │
│  - Action validation (can afford? legal move?)          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  SIMULATION LAYER (World State)                         │
│  - Entity state (position, inventory, health, AP)       │
│  - World state (tiles, chunks, time)                    │
│  - Physics/collision                                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  PERSISTENCE LAYER                                      │
│  - Save/load game state                                 │
│  - Chunk serialization                                  │
│  - Network synchronization (MMORPG mode)                │
└─────────────────────────────────────────────────────────┘
```

---

## Core Abstractions

### 1. Action System

**Everything is an Action:**
```python
class Action(ABC):
    action_type: ActionType
    ap_cost: int
    actor: Entity

    @abstractmethod
    def validate(self, game_state) -> bool

    @abstractmethod
    def execute(self, game_state) -> ActionResult

    @abstractmethod
    def to_dict(self) -> dict  # For networking/serialization
```

**Examples:**
- `MoveAction(actor, target_pos)` - AP cost: 1
- `AttackAction(actor, target)` - AP cost: 3-5
- `UseItemAction(actor, item, target)` - AP cost: varies
- `DigAction(actor, target_pos)` - AP cost: 2
- `WaitAction(actor)` - AP cost: 0 (passes turn)

**Benefits:**
- Single-player: Actions execute immediately after validation
- Multiplayer: Actions can be sent over network as packets
- AI: AI generates actions from behavior trees
- Pathfinding: Generate action queue (move, move, move, ...)
- Replay system: Record action sequence

### 2. Command System

**Input-Agnostic Commands:**
```python
class Command(ABC):
    @abstractmethod
    def to_action(self, game_state) -> Optional[Action]

# Concrete implementations
class MoveCommand(Command):
    direction: Vec2  # or target_pos for mouse click

class InteractCommand(Command):
    target_pos: Vec2
    interaction_type: str  # "dig", "pickup", "talk", etc.

class EndTurnCommand(Command):
    pass
```

**Input Sources:**
- **Keyboard:** Key press → MoveCommand(direction)
- **Mouse:** Click → MoveCommand(target_pos) OR InteractCommand
- **Network:** Packet → Command (deserialized)
- **AI:** Behavior tree → Command

### 3. Entity Update Tiers

**Tiered simulation for scalability:**

```python
class UpdateTier(Enum):
    FULL_SIMULATION = 0    # Active combat, nearby entities
    SIMPLIFIED = 1         # Loaded chunks, not in combat
    ABSTRACT = 2           # Near but unloaded
    TEMPLATE = 3           # Very distant, pure statistical
```

**Tier 0 - Full Simulation:**
- Every action validated and executed
- Full collision detection
- All game rules applied
- Used for: Player, active combatants, nearby NPCs

**Tier 1 - Simplified:**
- Actions still executed but with reduced checks
- Collision only with static geometry
- Used for: Loaded chunks outside active combat

**Tier 2 - Abstract:**
- High-level state updates (traveling, gathering, etc.)
- No per-frame updates
- Used for: Near chunks that might load soon

**Tier 3 - Template:**
- Statistical/deterministic outcomes
- "NPC X would be at position Y by time T"
- Re-simulate when player gets close
- Used for: Distant/unloaded areas

**MMORPG Evolution:**
- Server handles Tier 0/1 for all connected players
- Tier 2/3 become server zone management
- Each zone is a "shard" that can run on different servers

### 4. Time Management

**Unified Time System:**
```python
class GameTime:
    ticks: int           # Discrete time units
    seconds: float       # Real time (for animations)
    turn_number: int     # Current turn in combat

    TICKS_PER_SECOND = 60  # Configurable
```

**Time progression:**
- **Exploration mode:** Time advances by delta_time * TICKS_PER_SECOND
- **Combat mode:** Time advances by turn (e.g., 60 ticks per turn)
- **All AP costs** are in ticks (e.g., move = 60 ticks = 1 AP = 1 second)

**Benefits:**
- Consistent across real-time and turn-based
- Network sync uses ticks (not wall-clock time)
- Replay/determinism

### 5. Combat Manager

**Multiple concurrent combat instances:**
```python
class CombatInstance:
    instance_id: str
    combatants: List[Entity]
    initiative_order: Queue[Entity]
    current_turn: Entity
    turn_number: int
    is_active: bool

class CombatManager:
    active_combats: Dict[str, CombatInstance]

    def start_combat(self, initiator, targets) -> CombatInstance
    def add_combatant(self, combat_id, entity)
    def remove_combatant(self, combat_id, entity)
    def end_combat(self, combat_id)
```

**Combat scope:**
- Entities can be in exactly ONE combat instance
- New entities entering area join existing combat
- Combat ends when all hostiles dead/fled OR all allies dead/fled
- Multiple combats can occur simultaneously in different areas

**MMORPG Evolution:**
- Each combat instance can be on different server
- Server sends combat state updates to clients
- Client-side prediction for responsiveness

### 6. World Simulation Architecture

```python
class WorldManager:
    loaded_chunks: Dict[ChunkCoord, Chunk]
    entity_spatial_index: SpatialIndex  # Fast entity queries

    def update(self, delta_time):
        # Update entities by tier
        tier0_entities = self.get_tier0_entities()
        tier1_entities = self.get_tier1_entities()
        # ... tier2, tier3

        for entity in tier0_entities:
            entity.full_update(delta_time)

        for entity in tier1_entities:
            entity.simplified_update(delta_time)

        # Tier 2/3 updated less frequently (every N frames)
```

**Chunk System:**
```python
class Chunk:
    coord: ChunkCoord
    tiles: TileMap
    entities: List[Entity]
    is_loaded: bool
    is_modified: bool
    last_update_time: float

    def load(self):
        # Load from disk or generate procedurally

    def unload(self):
        # Serialize modified chunks to disk

    def get_update_tier(self, player_pos) -> UpdateTier:
        distance = self.distance_to(player_pos)
        # Determine tier based on distance
```

### 7. Cursor/Interaction System

**Multiple cursor modes:**
```python
class CursorMode(Enum):
    WALK = "walk"           # Movement cursor
    EXAMINE = "examine"     # Look/inspect
    INTERACT = "interact"   # Use/pickup/talk
    ATTACK = "attack"       # Hostile action
    TOOL = "tool"          # Context-sensitive (dig, harvest, etc.)
```

**Cursor → Command translation:**
```python
class CursorController:
    current_mode: CursorMode

    def on_click(self, world_pos) -> Command:
        if self.current_mode == CursorMode.WALK:
            return MoveCommand(target=world_pos)
        elif self.current_mode == CursorMode.EXAMINE:
            return ExamineCommand(target=world_pos)
        # etc...
```

**Input abstraction:**
- Keyboard: WASD → MoveCommand(direction)
- Mouse click: Click → depends on cursor mode
- Both can coexist and produce same Command types

---

## Implementation Strategy

### Phase 1: Core Abstractions (Now)
1. ✅ Action system base classes
2. ✅ Command system base classes
3. ✅ Action Point component
4. ✅ Time management system
5. ✅ Update tier enum and infrastructure

### Phase 2: Turn-Based Combat (Next)
1. Combat instance manager
2. Initiative system
3. Turn queue
4. Combat start/end triggers
5. AP-based movement in combat

### Phase 3: Pathfinding & Mouse Input
1. A* pathfinding system
2. Action queue for movement
3. Cursor system
4. Mouse input adapter
5. Click-to-move command generation

### Phase 4: World Simulation
1. Chunk loading/unloading
2. Entity spatial indexing
3. Tiered update system
4. Procedural generation

### Phase 5: Network Preparation (MMORPG Fork Point)
1. Action serialization
2. Command serialization
3. State synchronization protocol
4. Client-server architecture design

---

## Migration Paths

### Path 1: Isometric Single-Player → Isometric MMORPG
- Keep all core/ logic
- Replace input handlers with network client
- Add server that runs core/ as authoritative
- Clients send Commands, receive State updates

### Path 2: Isometric → 3D
- Keep all core/ logic
- Replace rendering/ with Unity/Godot/Unreal
- Isometric math → 3D transforms
- All game rules unchanged

### Path 3: Single-Player → 3D MMORPG
- Combine Path 1 + Path 2
- Server runs core/ logic in 3D space
- Clients render with 3D engine

**Key:** The `core/` layer never changes. Only presentation and input adapters change.

---

## Current State Refactoring Needs

### Immediate Changes:
1. **Add Action system** - Wrap all player actions (move, dig, etc.)
2. **Add ActionPoints component** - Track AP per entity
3. **Add Command layer** - Decouple input from game logic
4. **Add GameTime** - Unified time tracking
5. **Fix movement** - Use Action system with AP costs

### Files to Create:
- `core/actions/` - Action base classes and implementations
- `core/commands/` - Command base classes
- `core/time.py` - GameTime management
- `core/combat/` - Combat manager (Phase 2)

### Files to Modify:
- `core/game_state.py` - Add game mode, time management
- `core/systems/movement.py` - Convert to Action-based
- `core/entities/components.py` - Add ActionPoints component
- `main.py` - Use Command layer instead of direct commands

---

## Questions Before Implementation:

1. **Should I start with Phase 1 (Core Abstractions) now?** This means:
   - Creating Action/Command systems
   - Adding ActionPoints to entities
   - Refactoring current movement to use Actions
   - Not yet implementing combat, but preparing for it

2. **Movement fix priority:** Should I:
   - A) Quick-fix the current movement issue first, then refactor to Actions
   - B) Jump straight to Action-based movement (fixes the issue inherently)

3. **Time tracking:** Should turn-based combat use:
   - A) Action Points per turn (Fallout style: 10 AP, move costs 1, attack costs 3-5)
   - B) Action economy per turn (e.g., 1 move action + 1 standard action)
   - C) Time units (everything costs time, turn ends at 100 time units)

4. **AP regeneration in exploration:** Should AP:
   - A) Be infinite in exploration (only matters in combat)
   - B) Regenerate quickly in exploration (rate-limiting for movement speed)
   - C) Be the unified movement speed system (current movement_frequency becomes AP regen rate)

Let me know your thoughts and I'll proceed with implementation!

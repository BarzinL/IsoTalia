# Movement System Fix

## Current Problem

**Issue:** Rapid diagonal movement bypasses movement frequency limit.

### Current Flow (Broken)
```
Frame 1: Press W
  ↓
  KEYDOWN event → InputHandler → "move_north" command
  ↓
  GameState.process_command("move_north")
  ↓
  MovementSystem.process_movement_command() → Moves immediately
  ↓
  Player moves North

Frame 2: Press A (while W still held)
  ↓
  KEYDOWN event → InputHandler → "move_west" command
  ↓
  GameState.process_command("move_west")
  ↓
  MovementSystem.process_movement_command() → Moves immediately
  ↓
  Player moves West (bypassed timer!)

Frame 3: Press W again (rapid tap)
  ↓
  KEYDOWN event → "move_north" command
  ↓
  Moves immediately again! (bypassed timer!)
```

**Root cause:** `movement_timer` only applies to continuous held movement, not individual KEYDOWN events.

---

## Solution 1: Quick Fix (Band-Aid)

Add global cooldown in InputHandler:

```python
class InputHandler:
    def __init__(self):
        self.last_movement_time = 0.0
        self.movement_cooldown = 1.0 / DEFAULT_SETTINGS.movement_frequency

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_map and event.key in self.movement_keys:
                current_time = pygame.time.get_ticks() / 1000.0

                # Check global movement cooldown
                if current_time - self.last_movement_time >= self.movement_cooldown:
                    commands.append(self.key_map[event.key])
                    self.last_movement_time = current_time
                else:
                    # Ignore this input, too soon!
                    pass
```

**Pros:** Quick, minimal code change
**Cons:** Still coupled to input layer, hard to extend

---

## Solution 2: Action System (Proper Fix)

### New Flow with Actions

```
Frame 1: Press W
  ↓
  KEYDOWN event → InputHandler
  ↓
  Creates: MoveCommand(direction=(0, -1))
  ↓
  Command → Action Converter
  ↓
  Creates: MoveAction(actor=player, direction=(0, -1))
  ↓
  Action Validator checks:
    - Does player have enough AP? ✓
    - Is tile walkable? ✓
    - Is action legal in current mode? ✓
  ↓
  Action Executor:
    - Spend 60 ticks (1 AP)
    - Move player
    - Publish ENTITY_MOVED event
  ↓
  Player AP: 240 → 180 (assuming 4 AP per second regen)

Frame 2: Press A (0.05 seconds later, rapid tap)
  ↓
  KEYDOWN event → InputHandler
  ↓
  Creates: MoveCommand(direction=(-1, 0))
  ↓
  Creates: MoveAction(actor=player, direction=(-1, 0))
  ↓
  Action Validator checks:
    - Does player have enough AP?
      Current AP: 180 ticks
      Cost: 60 ticks
      Regen since last move: 3 ticks (0.05s * 60 ticks/s)
      Total: 183 ticks
      ✓ Enough!
  ↓
  Action Executor:
    - Spend 60 ticks
    - Move player
  ↓
  Player AP: 183 → 123

Frame 3: Press W again (0.05 seconds later, rapid tap)
  ↓
  KEYDOWN event → InputHandler
  ↓
  Creates: MoveCommand(direction=(0, -1))
  ↓
  Creates: MoveAction(actor=player, direction=(0, -1))
  ↓
  Action Validator checks:
    - Does player have enough AP?
      Current AP: 123 ticks
      Cost: 60 ticks
      Regen: 3 ticks
      Total: 126 ticks
      ✓ Enough!
  ↓
  Action Executor:
    - Spend 60 ticks
    - Move player
  ↓
  Player AP: 126 → 66

Frame 4: Press A again (0.05 seconds later, rapid tap)
  ↓
  KEYDOWN event → InputHandler
  ↓
  Creates: MoveCommand(direction=(-1, 0))
  ↓
  Creates: MoveAction(actor=player, direction=(-1, 0))
  ↓
  Action Validator checks:
    - Does player have enough AP?
      Current AP: 66 ticks
      Cost: 60 ticks
      Regen: 3 ticks
      Total: 69 ticks
      ✓ BARELY enough!
  ↓
  Move succeeds

Frame 5: Press W again (0.05 seconds later, STILL rapid tapping)
  ↓
  KEYDOWN event → InputHandler
  ↓
  Creates: MoveCommand(direction=(0, -1))
  ↓
  Creates: MoveAction(actor=player, direction=(0, -1))
  ↓
  Action Validator checks:
    - Does player have enough AP?
      Current AP: 9 ticks
      Cost: 60 ticks
      Regen: 3 ticks
      Total: 12 ticks
      ✗ NOT ENOUGH!
  ↓
  Action REJECTED
  ↓
  NO MOVEMENT (player must wait for AP to regenerate)
```

**Result:** Natural rate-limiting via AP system!

---

## Action Point Mechanics

### Configuration
```python
# In core/settings.py
@dataclass
class GameSettings:
    # Action Point settings
    base_ap_pool: int = 240           # 4 seconds worth at 60 ticks/s
    ap_regen_rate: int = 60           # 60 ticks per second = 1 AP/s

    # Action costs (in ticks)
    move_cost: int = 60               # 1 AP = 1 second
    attack_cost: int = 120            # 2 AP
    dig_cost: int = 120               # 2 AP
    use_item_cost: int = 60           # 1 AP
```

### In Exploration Mode
- AP pool: 240 ticks (4 seconds of movement buffered)
- Regen: 60 ticks/second
- If you tap move 4 times rapidly: Works
- If you tap move 5 times rapidly: 5th move fails (AP depleted)
- After 1 second of no movement: Pool refills to max

**Effect:** Smooth movement with natural rhythm, but can't spam infinitely fast.

### In Combat Mode
- AP pool: Refreshes to MAX at start of turn (e.g., 240 ticks = 4 AP)
- NO regen during turn
- Move costs 60 ticks (1 AP)
- Attack costs 120 ticks (2 AP)
- You can: Move 4 times, OR Move 2 times + Attack, OR Attack 2 times

**Effect:** Classic turn-based AP system like Fallout.

---

## Implementation

### 1. Add ActionPoints Component
```python
# core/entities/components.py

@dataclass
class ActionPoints:
    """Action point tracking for entities."""
    current: int
    maximum: int
    regen_rate: int  # Ticks per second (0 in combat mode)

    def can_afford(self, cost: int) -> bool:
        return self.current >= cost

    def spend(self, cost: int) -> bool:
        if self.can_afford(cost):
            self.current -= cost
            return True
        return False

    def regenerate(self, delta_ticks: int):
        """Regenerate AP (used in exploration mode)."""
        self.current = min(self.maximum, self.current + delta_ticks)

    def reset_to_max(self):
        """Reset AP to maximum (used at start of combat turn)."""
        self.current = self.maximum
```

### 2. Create Action Base Class
```python
# core/actions/base.py

class Action(ABC):
    """Base class for all game actions."""

    def __init__(self, actor: Entity):
        self.actor = actor
        self.ap_cost = self.get_ap_cost()

    @abstractmethod
    def get_ap_cost(self) -> int:
        """Return AP cost in ticks."""
        pass

    @abstractmethod
    def validate(self, game_state) -> ActionResult:
        """Check if action can be performed."""
        pass

    @abstractmethod
    def execute(self, game_state) -> ActionResult:
        """Perform the action."""
        pass
```

### 3. Create MoveAction
```python
# core/actions/movement.py

class MoveAction(Action):
    def __init__(self, actor: Entity, direction: tuple):
        self.direction = direction
        super().__init__(actor)

    def get_ap_cost(self) -> int:
        from ..settings import DEFAULT_SETTINGS
        return DEFAULT_SETTINGS.move_cost

    def validate(self, game_state) -> ActionResult:
        # Check AP
        ap = self.actor.get_component(ActionPoints)
        if not ap or not ap.can_afford(self.ap_cost):
            return ActionResult(success=False, reason="Not enough AP")

        # Check if move is legal
        pos = self.actor.get_component(Position)
        target_x = pos.x + self.direction[0]
        target_y = pos.y + self.direction[1]

        if not game_state.movement_system.can_move_to(self.actor, target_x, target_y):
            return ActionResult(success=False, reason="Cannot move there")

        return ActionResult(success=True)

    def execute(self, game_state) -> ActionResult:
        # Spend AP
        ap = self.actor.get_component(ActionPoints)
        ap.spend(self.ap_cost)

        # Perform move
        success = game_state.movement_system.move_entity(
            self.actor, self.direction[0], self.direction[1]
        )

        if success:
            # Publish event
            pos = self.actor.get_component(Position)
            game_state.event_bus.publish(Event(
                EventType.ENTITY_MOVED,
                {'entity_id': self.actor.id, 'x': pos.x, 'y': pos.y}
            ))

        return ActionResult(success=success)
```

### 4. Update GameState
```python
# core/game_state.py

def update(self, delta_time: float):
    # Update game time
    delta_ticks = int(delta_time * 60)  # 60 ticks per second
    self.game_time += delta_time

    # Regenerate AP for all entities in exploration mode
    if self.game_mode == GameMode.EXPLORATION:
        for entity in self.entity_manager.get_all_entities():
            ap = entity.get_component(ActionPoints)
            if ap and ap.regen_rate > 0:
                regen_amount = int(delta_time * ap.regen_rate)
                ap.regenerate(regen_amount)

def process_action(self, action: Action) -> ActionResult:
    """Process any action through unified system."""
    # Validate
    result = action.validate(self)
    if not result.success:
        return result

    # Execute
    result = action.execute(self)
    return result
```

### 5. Update Input Handler
```python
# main.py

class InputHandler:
    def process_event(self, event):
        commands = []

        if event.type == pygame.KEYDOWN:
            if event.key in self.key_map:
                # Create command, not execute directly
                commands.append(self.key_map[event.key])

        return commands

class Game:
    def _process_command(self, command: str):
        # Convert command string to Command object
        if command.startswith('move_'):
            direction = self._get_direction_from_command(command)
            cmd = MoveCommand(direction=direction)
        # ... other commands

        # Convert Command to Action
        action = cmd.to_action(self.game_state, self.game_state.player_entity)

        # Process through action system
        result = self.game_state.process_action(action)

        if not result.success:
            # Could show feedback to player
            print(f"Action failed: {result.reason}")
```

---

## Benefits of Action System

1. **Natural rate limiting** - AP system prevents spam
2. **Unified system** - Movement, combat, digging all use same pattern
3. **Network ready** - Actions can be serialized/deserialized
4. **Replay system** - Record action sequence, replay later
5. **AI ready** - AI generates Actions, same validation
6. **Predictable** - Always behaves the same way
7. **Testable** - Easy to unit test action logic

---

## Migration Strategy

### Option A: Quick Fix First
1. Add cooldown to InputHandler (1 hour)
2. Test and verify fix (30 min)
3. Then refactor to Actions (4-6 hours)

**Total:** ~6 hours, but game is playable after 1.5 hours

### Option B: Jump to Actions
1. Create Action system (2 hours)
2. Create ActionPoints component (1 hour)
3. Refactor movement to use Actions (2 hours)
4. Update GameState and input handling (1 hour)
5. Test and debug (1 hour)

**Total:** ~7 hours, but cleaner result

**Recommendation:** Option B - The Action system is foundational for everything else (combat, pathfinding, multiplayer). Worth doing right from the start.

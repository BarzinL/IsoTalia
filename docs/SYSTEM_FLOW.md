# IsoTalia System Flow Diagrams

## Current System (MVP)

```
Keyboard Press
      ↓
InputHandler.process_event()
      ↓
Returns command string ("move_north")
      ↓
Game._process_command()
      ↓
GameState.process_command()
      ↓
MovementSystem.process_movement_command()
      ↓
MovementSystem.move_entity() - Validates & moves
      ↓
Updates Entity.Position component
      ↓
Publishes ENTITY_MOVED event
```

**Problem:** Input → Directly to game logic, no abstraction for other input types

---

## Target System (Action-Based)

```
┌─────────────┐
│ Input Layer │
└─────────────┘
      ↓
┌─────────────────────────────────────┐
│  Keyboard  │  Mouse  │  Network     │
│  Handler   │  Handler│  Handler     │
└─────────────────────────────────────┘
      ↓            ↓           ↓
┌─────────────────────────────────────┐
│       Command Factory               │
│  - MoveCommand(direction/target)    │
│  - InteractCommand(type, target)    │
│  - AttackCommand(target)            │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│      Command Validator              │
│  - Check if valid for current mode  │
│  - Check if entity can act          │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│      Command → Action Converter     │
│  MoveCommand → MoveAction(pos)      │
│  (may generate action queue for     │
│   pathfinding)                      │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│      Action Validator               │
│  - Check AP cost                    │
│  - Check preconditions              │
│  - Check legality (collision, etc)  │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│      Action Executor                │
│  - Spend AP                         │
│  - Update game state                │
│  - Trigger effects                  │
│  - Publish events                   │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│      Event System                   │
│  - Broadcast state changes          │
│  - Update UI                        │
│  - Trigger reactions (AI, etc)      │
└─────────────────────────────────────┘
```

**Benefits:**
- Mouse click → MoveCommand → MoveAction (same as keyboard)
- Network packet → MoveCommand → MoveAction (same as local)
- AI decision → MoveCommand → MoveAction (same as player)
- Pathfinding → Queue of MoveActions
- All validation in one place
- Easy to add new input methods

---

## Game Mode State Machine

```
┌─────────────────────┐
│  EXPLORATION MODE   │
│                     │
│ - AP regenerates    │
│ - Movement rate-    │
│   limited by AP     │
│ - Can save/load     │
└─────────────────────┘
         ↕
    [Combat Trigger]
    - Enemy spots player
    - Player attacks
    - Hostile NPC triggered
         ↓
┌─────────────────────┐
│    COMBAT MODE      │
│                     │
│ - Turn-based        │
│ - Fixed AP per turn │
│ - Initiative order  │
│ - Cannot save       │
└─────────────────────┘
         ↕
    [Combat Ends]
    - All enemies defeated
    - All allies dead
    - Fled successfully
         ↓
┌─────────────────────┐
│  EXPLORATION MODE   │
└─────────────────────┘
```

---

## Entity Update Flow

```
┌─────────────────────────────────────────────────┐
│             WorldManager.update()               │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Spatial Query: Get entities near player        │
└─────────────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
┌───────────────┐      ┌───────────────┐
│  TIER 0       │      │  TIER 1       │
│  Full Sim     │      │  Simplified   │
│               │      │               │
│ - In combat   │      │ - Loaded but  │
│ - Near player │      │   not combat  │
│ - Full checks │      │ - Reduced     │
│               │      │   checks      │
└───────────────┘      └───────────────┘
        ↓                       ↓
┌───────────────────────────────────────┐
│  Action System processes queued       │
│  actions for each entity              │
└───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────┐
│  Update components (position, health, │
│  inventory, etc.)                     │
└───────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────┐
│  Publish events for state changes     │
└───────────────────────────────────────┘
```

**Distant entities (Tier 2/3):**
- Updated on longer intervals (every 10 frames, 100 frames, etc.)
- Use statistical/template-based updates
- "Catch up" when player gets close

---

## Combat Flow

```
[Combat Triggered]
        ↓
┌─────────────────────────────────────┐
│  1. Create CombatInstance           │
│     - Roll initiative for all       │
│     - Sort by initiative order      │
│     - Set first combatant active    │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│  2. Begin Turn                      │
│     - Reset AP for current entity   │
│     - Enable actions for entity     │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│  3. Process Actions                 │
│     - Entity performs actions       │
│     - Spend AP per action           │
│     - Continue until AP exhausted   │
│       or "End Turn" chosen          │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│  4. End Turn                        │
│     - Apply end-of-turn effects     │
│     - Check for combat end          │
│       conditions                    │
└─────────────────────────────────────┘
        ↓
   [More turns?]
        ↓
┌─────────────────────────────────────┐
│  5. Next Combatant                  │
│     - Move to next in initiative    │
│     - Loop back to step 2           │
└─────────────────────────────────────┘
        ↓
   [Combat End Condition Met]
        ↓
┌─────────────────────────────────────┐
│  6. End Combat                      │
│     - Cleanup combat instance       │
│     - Award XP/loot                 │
│     - Return to exploration mode    │
└─────────────────────────────────────┘
```

**Mid-Combat Joins:**
- New entity enters area
- Check if hostile to any combatant
- If yes: roll initiative, insert into turn order
- Gets full AP next time their turn comes up

---

## Chunk Loading Flow

```
    Player moves
         ↓
┌────────────────────────┐
│ Check player position  │
└────────────────────────┘
         ↓
┌────────────────────────────────────┐
│ Calculate required chunks          │
│ (radius around player)             │
└────────────────────────────────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌────────┐  ┌────────┐
│ Load   │  │ Unload │
│ New    │  │ Distant│
│ Chunks │  │ Chunks │
└────────┘  └────────┘
    ↓            ↓
┌────────┐  ┌────────┐
│ Check  │  │ Save   │
│ if in  │  │ if     │
│ save   │  │ modif. │
└────────┘  └────────┘
    ↓            ↓
┌────────┐  ┌────────┐
│ Load   │  │ Ser-   │
│ from   │  │ ialize │
│ disk   │  │ to disk│
└────────┘  └────────┘
    ↓
┌──────────────────┐
│ Generate         │
│ procedurally     │
│ if new           │
└──────────────────┘
    ↓
┌──────────────────┐
│ Activate chunk   │
│ Add to active    │
│ chunks dict      │
└──────────────────┘
```

---

## Network Architecture (MMORPG Fork)

### Server Architecture
```
┌─────────────────────────────────────┐
│          Game Server                │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Authoritative GameState      │ │
│  │  - World state                │ │
│  │  - All entities               │ │
│  │  - Combat instances           │ │
│  └───────────────────────────────┘ │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │  Action Validator/Executor    │ │
│  └───────────────────────────────┘ │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │  State Synchronizer           │ │
│  │  - Sends state updates to     │ │
│  │    clients                    │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
            ↕ (Network)
┌─────────────────────────────────────┐
│          Game Client                │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  Input Handler                │ │
│  │  - Keyboard/Mouse             │ │
│  └───────────────────────────────┘ │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │  Command Generator            │ │
│  │  - Sends commands to server   │ │
│  └───────────────────────────────┘ │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │  Client-Side Prediction       │ │
│  │  - Predicts result locally    │ │
│  │  - Reconciles with server     │ │
│  └───────────────────────────────┘ │
│              ↓                      │
│  ┌───────────────────────────────┐ │
│  │  Rendering Layer              │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Protocol:**
1. Client sends Command (serialized)
2. Server validates Command
3. Server converts to Action
4. Server executes Action
5. Server broadcasts State update
6. Client reconciles prediction with server state
7. Client renders

**Key:** Same `core/` code runs on both client and server!

---

## File Structure Evolution

### Current (MVP)
```
IsoTalia/
├── core/
│   ├── world/
│   ├── entities/
│   ├── systems/
│   ├── game_state.py
│   └── events.py
├── rendering/
└── main.py
```

### Phase 1 (Actions & Commands)
```
IsoTalia/
├── core/
│   ├── actions/           # NEW
│   │   ├── base.py
│   │   ├── movement.py
│   │   ├── interaction.py
│   │   └── combat.py
│   ├── commands/          # NEW
│   │   ├── base.py
│   │   └── implementations.py
│   ├── time.py           # NEW
│   ├── world/
│   ├── entities/
│   ├── systems/
│   ├── game_state.py
│   └── events.py
├── rendering/
└── main.py
```

### Phase 2 (Combat)
```
IsoTalia/
├── core/
│   ├── actions/
│   ├── commands/
│   ├── combat/            # NEW
│   │   ├── combat_state.py
│   │   ├── initiative.py
│   │   └── combat_manager.py
│   ├── time.py
│   ├── world/
│   ├── entities/
│   ├── systems/
│   ├── game_state.py
│   └── events.py
├── rendering/
└── main.py
```

### Phase 5 (Network Ready)
```
IsoTalia/
├── core/                  # Runs on BOTH client & server
│   ├── actions/
│   ├── commands/
│   ├── combat/
│   ├── time.py
│   ├── world/
│   ├── entities/
│   ├── systems/
│   ├── game_state.py
│   └── events.py
├── network/               # NEW
│   ├── protocol.py
│   ├── serialization.py
│   ├── client.py
│   └── server.py
├── rendering/
├── main.py                # Single-player
├── client_main.py         # NEW - Multiplayer client
└── server_main.py         # NEW - Multiplayer server
```

**Fork Points:**
- `main.py` - Original single-player
- `client_main.py` + `server_main.py` - MMORPG version
- Both use same `core/`!

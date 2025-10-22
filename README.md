# IsoTalia

A 3D isometric post-apocalyptic role-playing game built with PyGame CE.

## Overview

IsoTalia is designed with a clean separation between game logic and rendering, making it easy to port to different engines and frameworks. The core game engine is completely framework-agnostic, while PyGame CE is used as the initial rendering backend.

## Architecture

### Core Engine (Framework-Agnostic)
- `core/world/` - Tile map system and terrain definitions
- `core/entities/` - Entity-component system
- `core/systems/` - Game systems (movement, interaction)
- `core/events.py` - Event bus for decoupled communication
- `core/game_state.py` - Main game state orchestrator

### Rendering Backend (PyGame CE)
- `rendering/isometric.py` - Isometric coordinate conversion
- `rendering/pygame_renderer.py` - PyGame-specific renderer
- `rendering/sprite_manager.py` - Asset management and placeholder generation

### Data
- `data/tiles.json` - Tile type definitions
- `data/items.json` - Item and tool definitions

## Features (MVP)

- ✅ Isometric grid-based world (32x16 pixel tiles)
- ✅ Grid-locked player movement
- ✅ Digging/harvesting system with tools
- ✅ Resource collection
- ✅ Multiple tile types (walkable, obstacles, hazards)
- ✅ Camera system that follows player
- ✅ Event-driven architecture
- ✅ Placeholder sprite generation

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

- **WASD / Arrow Keys** - Move player
- **Space** - Dig tile (north of player)
- **F3** - Toggle debug overlay
- **ESC** - Quit game

## Development Philosophy

The game is built with portability in mind:

1. **Core logic** is completely independent of PyGame
2. **Data-driven design** allows easy modding via JSON files
3. **Clean interfaces** between systems enable easy testing
4. **Event-based communication** reduces coupling
5. **Just-in-time optimization** - implement performance-critical parts in C/Rust when needed

## Future Enhancements

- Multi-level Z-axis support (digging down/building up)
- Advanced AI and NPC systems
- Crafting and building systems
- Procedural world generation
- Multiplayer/networking support
- Migration to 3D engine (Unity/Godot)

## Project Structure

```
IsoTalia/
├── core/              # Framework-agnostic engine
│   ├── world/         # Tile map and terrain
│   ├── entities/      # Entity-component system
│   ├── systems/       # Game systems
│   ├── events.py      # Event bus
│   └── game_state.py  # Main game state
├── rendering/         # PyGame-specific rendering
├── data/              # JSON game data
├── assets/            # Sprites and audio
├── tests/             # Unit tests
└── main.py            # Entry point
```

## License

MIT License - See LICENSE file for details

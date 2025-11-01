# IsoTalia

[![CI/CD Pipeline](https://github.com/isotalia/isotalia/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/isotalia/isotalia/actions)
[![Code Quality](https://github.com/isotalia/isotalia/workflows/Code%20Quality/badge.svg)](https://github.com/isotalia/isotalia/actions)
[![Test Coverage](https://codecov.io/gh/isotalia/isotalia/branch/main/graph/badge.svg)](https://codecov.io/gh/isotalia/isotalia)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A 3D isometric post-apocalyptic role-playing game built with PyGame CE, featuring enterprise-grade development practices and framework-agnostic architecture.

## Overview

IsoTalia is designed with a clean separation between game logic and rendering, making it easy to port to different engines and frameworks. The core game engine is completely framework-agnostic, while PyGame CE is used as the initial rendering backend. Built with professional development standards including automated testing, code quality enforcement, and continuous integration.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/isotalia/isotalia.git
cd isotalia

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run the game
python main.py
```

### Development Setup

For full development environment setup, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Architecture

### Core Engine (Framework-Agnostic)
- `core/world/` - Tile map system and terrain definitions
- `core/entities/` - Entity-component system with comprehensive testing
- `core/systems/` - Game systems (movement, interaction)
- `core/events.py` - Event bus for decoupled communication with type-safe events
- `core/game_state.py` - Main game state orchestrator
- `core/settings.py` - Configuration management

### Rendering Backend (PyGame CE)
- `rendering/isometric.py` - Isometric coordinate conversion
- `rendering/pygame_renderer.py` - PyGame-specific renderer
- `rendering/sprite_manager.py` - Asset management and placeholder generation

### Data
- `data/tiles.json` - Tile type definitions
- `data/items.json` - Item and tool definitions

## ✨ Features (Current)

### Gameplay
- ✅ Isometric grid-based world (32x16 pixel tiles)
- ✅ Grid-locked player movement with continuous input handling
- ✅ Digging/harvesting system with tools
- ✅ Resource collection and inventory management
- ✅ Multiple tile types (walkable, obstacles, hazards)
- ✅ Camera system that follows player
- ✅ Event-driven architecture with type-safe event system
- ✅ Placeholder sprite generation
- ✅ Professional game state management

### Development Infrastructure
- ✅ **CI/CD Pipeline**: Automated testing, linting, and deployment
- ✅ **Code Quality**: Black formatting, Ruff linting, MyPy type checking
- ✅ **Comprehensive Testing**: 80%+ coverage with pytest, automated in CI
- ✅ **Pre-commit Hooks**: Automated code quality checks
- ✅ **Multi-version Testing**: Python 3.8-3.12 compatibility
- ✅ **Security Scanning**: Automated security vulnerability detection
- ✅ **Performance Testing**: Automated performance regression detection

### Architecture
- ✅ **Framework Agnostic**: Core engine independent of rendering/input frameworks
- ✅ **Event System**: Type-safe, immutable event system with comprehensive testing
- ✅ **Entity-Component System**: Modern, testable architecture
- ✅ **Data-Driven Design**: JSON-based configuration for easy modding
- ✅ **Clean Interfaces**: Well-defined boundaries between systems

## 🎮 Controls

- **WASD / Arrow Keys** - Move player
- **Space** - Dig tile (north of player)
- **F3** - Toggle debug overlay
- **ESC** - Quit game

## 🛠️ Development

### Code Quality Standards

This project enforces high code quality standards through automated tools:

- **Black**: Automatic code formatting (88 character line length)
- **Ruff**: Fast Python linting with 100+ rules enabled
- **MyPy**: Static type checking for better code reliability
- **Pre-commit**: Automated quality checks before commits
- **Testing**: Minimum 80% test coverage requirement

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=core --cov=rendering

# Run specific test categories
pytest -m unit        # Unit tests
pytest -m integration # Integration tests
pytest -m slow        # Performance tests

# Generate HTML coverage report
pytest --cov=core --cov-report=html
```

### Code Quality Checks

```bash
# Format code
black .

# Check code quality
ruff check .

# Type checking
mypy core/ rendering/

# Run all quality checks
pre-commit run --all-files
```

## 🔮 Development Philosophy

The game is built with portability and maintainability in mind:

1. **Framework Agnostic**: Core logic completely independent of PyGame
2. **Data-Driven**: Easy modding via JSON configuration files
3. **Event-Driven**: Loose coupling through type-safe event system
4. **Test-First**: Comprehensive testing with automated CI validation
5. **Quality-Focused**: Automated code quality enforcement
6. **Just-in-Time Optimization**: Performance profiling before optimization

## 📈 Project Status

**Current Phase**: Alpha Development (v0.1.0)
- Core engine architecture established
- Professional development infrastructure operational
- MVP gameplay features implemented
- Comprehensive testing framework active

**Development Priority**: Core gameplay mechanics and systems refinement

## 🚧 Future Enhancements

### Near Term (v0.2-0.5)
- Multi-level Z-axis support (digging down/building up)
- Enhanced AI and NPC systems
- Improved asset management and sprite system
- Performance optimization for larger maps

### Medium Term (v1.0)
- Crafting and building systems
- Procedural world generation
- Save/load game functionality
- Enhanced user interface

### Long Term (v2.0+)
- Multiplayer/networking support
- Migration to 3D engine (Unity/Godot/Unreal)
- Advanced modding support
- Mobile platform support

## 🏗️ Project Structure

```
IsoTalia/
├── .github/workflows/      # CI/CD pipeline configuration
├── core/                  # Framework-agnostic engine
│   ├── world/             # Tile map and terrain systems
│   ├── entities/          # Entity-component system
│   ├── systems/           # Game systems (movement, interaction)
│   ├── events.py          # Type-safe event bus
│   ├── game_state.py      # Main game state orchestrator
│   └── settings.py        # Configuration management
├── rendering/             # PyGame-specific rendering
├── data/                  # JSON game data
├── tests/                 # Comprehensive test suite
│   ├── conftest.py        # Pytest fixtures and configuration
│   ├── unit/              # Unit tests with 80%+ coverage
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data and fixtures
├── docs/                  # Development documentation
├── .pre-commit-config.yaml # Automated quality checks
├── pyproject.toml         # Project configuration
└── main.py                # Game entry point
```

## 🤝 Contributing

We welcome contributions! Please read our [Development Guide](docs/DEVELOPMENT.md) for detailed setup instructions and coding standards.

### Contribution Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all quality checks pass (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards
- Follow Black formatting (automatically enforced)
- Pass Ruff linting checks (comprehensive rule set)
- Add MyPy type hints where applicable
- Write comprehensive tests for new functionality
- Maintain 80%+ test coverage
- Update documentation as needed

## 📚 Documentation

- [Development Guide](docs/DEVELOPMENT.md) - Comprehensive development setup and guidelines
- [Architecture Overview](docs/ARCHITECTURE.md) - Technical architecture and design decisions
- [API Documentation](docs/api/) - Generated API documentation (coming soon)

## 📊 Build Status

| Component | Status |
|-----------|--------|
| CI/CD Pipeline | ✅ Active |
| Code Quality | ✅ Enforced |
| Test Coverage | ✅ 80%+ Required |
| Multi-version Testing | ✅ Python 3.8-3.12 |
| Security Scanning | ✅ Active |
| Performance Testing | ✅ Included |

## 📄 License

AGPLv3 License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PyGame CE community for the excellent game development framework
- Black, Ruff, and MyPy teams for outstanding developer tools
- GitHub Actions for robust CI/CD capabilities
- The open-source Python ecosystem for making this project possible

---

**Built with ❤️ by the IsoTalia Development Team**

*For questions, discussions, or contributions, please visit our [GitHub repository](https://github.com/isotalia/isotalia).*

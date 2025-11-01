# IsoTalia Development Guide

## Overview

This guide provides comprehensive information for developers working on the IsoTalia project. It covers setup, development workflows, testing, and contribution guidelines.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Code Quality Tools](#code-quality-tools)
3. [Testing](#testing)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Development Workflow](#development-workflow)
6. [Architecture Guidelines](#architecture-guidelines)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/isotalia/isotalia.git
   cd isotalia
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Run the development environment check:**
   ```bash
   python -m pytest tests/ -v
   ```

## Code Quality Tools

### Black (Code Formatting)

Black is configured to automatically format your code according to PEP 8 standards.

**Usage:**
```bash
# Format all files
black .

# Check formatting without making changes
black --check .

# Format specific files
black core/ rendering/
```

**Configuration:**
- Line length: 88 characters
- Target Python versions: 3.8-3.12
- Automatic file detection with exclusions for build artifacts

### Ruff (Linting and Import Sorting)

Ruff provides comprehensive linting, import sorting, and code analysis.

**Usage:**
```bash
# Check all issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format imports
ruff check --select I .

# Check specific directories
ruff check core/ rendering/
```

**Rules enabled:**
- pycodestyle (E, W)
- pyflakes (F)
- pyupgrade (UP)
- flake8-bugbear (B)
- flake8-simplify (SIM)
- isort (I)
- pep8-naming (N)
- And many more for comprehensive code quality

### MyPy (Type Checking)

MyPy provides static type checking for better code reliability.

**Usage:**
```bash
# Type check core modules
mypy core/ rendering/

# Type check with strict settings
mypy --strict core/
```

### Pre-commit Hooks

Pre-commit hooks automatically run quality checks before each commit.

**Installation:**
```bash
pre-commit install
```

**Manual execution:**
```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files core/settings.py
```

## Testing

### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and shared fixtures
├── unit/               # Unit tests for individual components
│   ├── test_events.py
│   ├── test_entities.py
│   ├── test_world.py
│   └── test_game_state.py
├── integration/        # Integration tests
└── fixtures/          # Test data and fixtures
```

### Running Tests

**All tests:**
```bash
pytest
```

**With coverage report:**
```bash
pytest --cov=core --cov=rendering --cov-report=html
```

**Specific test categories:**
```bash
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m slow        # Slow running tests
```

**Specific test files:**
```bash
pytest tests/unit/test_entities.py
```

**Verbose output:**
```bash
pytest -v
```

**Stop on first failure:**
```bash
pytest -x
```

### Test Coverage

**Generate coverage report:**
```bash
pytest --cov=core --cov=rendering --cov-report=term-missing
```

**View HTML coverage report:**
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Coverage thresholds:**
- Minimum 80% coverage required
- Report shows missed lines in HTML format
- CI pipeline fails if coverage drops below threshold

### Writing Tests

**Unit test example:**
```python
import pytest
from core.entities.entity import Entity

def test_entity_creation():
    """Test that entities can be created."""
    entity = Entity()
    assert entity.id is not None
    assert len(entity._components) == 0

def test_entity_with_specific_id():
    """Test entity creation with specific ID."""
    entity = Entity(entity_id=42)
    assert entity.id == 42
```

**Using fixtures:**
```python
def test_something(mock_game_state):
    """Test using a pre-configured game state."""
    # mock_game_state is automatically provided by conftest.py
    assert mock_game_state.is_running is False
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline runs automatically on:
- Push to main/develop branches
- Pull requests to main branch
- Releases

**Pipeline stages:**
1. **Quality Checks**: Black, Ruff, MyPy, security scanning
2. **Multi-version Testing**: Python 3.8-3.12
3. **Game Engine Tests**: Core functionality validation
4. **Documentation**: Docstring and documentation generation
5. **Performance Tests**: Performance benchmarks
6. **Build and Release**: Automated packaging (on releases)

### Manual Pipeline Execution

**Trigger full pipeline:**
```bash
# Push changes to trigger CI
git push origin feature/your-feature

# Or create a pull request
```

## Development Workflow

### Feature Development

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write code with tests:**
   - Follow style guidelines (Black + Ruff)
   - Write comprehensive unit tests
   - Update documentation

3. **Run quality checks:**
   ```bash
   black .
   ruff check .
   pytest
   pre-commit run --all-files
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/your-feature-name
   ```

5. **Create pull request:**
   - Include description of changes
   - Reference any related issues
   - Ensure all CI checks pass

### Commit Message Convention

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(game-state): add new game mode support
fix(entities): resolve memory leak in entity cleanup
docs(readme): update installation instructions
test(world): add tile map boundary tests
```

## Architecture Guidelines

### Code Organization

**Core Principles:**
1. **Framework Agnostic**: Keep core/ independent of rendering/input frameworks
2. **Event-Driven**: Use events for loose coupling between systems
3. **Component-Based**: Use ECS architecture for entities
4. **Data-Driven**: Configuration in JSON files when possible

**Directory Structure:**
```
core/                  # Framework-agnostic game logic
├── entities/         # Entity-component system
├── systems/          # Game systems (movement, interaction, etc.)
├── world/           # Tile map and terrain
├── events.py        # Event bus and definitions
├── game_state.py    # Main game state orchestrator
└── settings.py      # Configuration management

rendering/            # PyGame-specific rendering
├── pygame_renderer.py
├── isometric.py
└── sprite_manager.py

data/                 # Game data (JSON configuration)
├── tiles.json
└── items.json
```

### Adding New Features

**For new game systems:**
1. Create system class in `core/systems/`
2. Add to `GameState.__init__()`
3. Write comprehensive unit tests
4. Update documentation

**For new entities/components:**
1. Add component definitions in `core/entities/components.py`
2. Update `core/entities/player.py` if needed
3. Write component tests
4. Update documentation

**For new tile types:**
1. Add to `data/tiles.json`
2. Update `core/world/terrain.py` if needed
3. Add tests for new behavior
4. Update documentation

### Performance Considerations

1. **Avoid premature optimization**
2. **Profile before optimizing**
3. **Use appropriate data structures**
4. **Cache expensive calculations**
5. **Consider memory usage**

## Common Tasks

### Adding New Dependencies

1. **Add to requirements:**
   ```bash
   pip install package-name
   pip freeze > requirements.txt  # Update lock file
   ```

2. **Update pyproject.toml:**
   ```toml
   [project.optional-dependencies]
   dev = [
       "package-name>=1.0.0",
   ]
   ```

3. **Update documentation**

### Running the Game

**Development mode:**
```bash
python main.py
```

**With debug output:**
```bash
python main.py --debug
```

### Debug Configuration

**VS Code launch.json:**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run IsoTalia",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## Troubleshooting

### Common Issues

**Import errors:**
- Ensure virtual environment is activated
- Check Python path includes project root
- Verify all dependencies are installed

**Test failures:**
- Check for import errors in test files
- Verify fixtures are properly defined
- Run tests individually to isolate issues

**Pre-commit hook failures:**
- Run `black .` to fix formatting
- Run `ruff check --fix .` to fix linting issues
- Check MyPy type errors

**CI pipeline failures:**
- Check workflow logs in GitHub Actions
- Ensure all tests pass locally
- Verify coverage meets thresholds

### Getting Help

1. **Check existing documentation**
2. **Review test examples**
3. **Search GitHub issues**
4. **Ask on GitHub Discussions**
5. **Contact development team**

### Performance Issues

**Profiling:**
```bash
# Install profiling tools
pip install memory-profiler psutil

# Profile memory usage
python -m memory_profiler main.py

# Profile CPU usage
python -c "import cProfile; cProfile.run('main()')"
```

**Performance testing:**
```bash
# Run performance tests
pytest tests/unit/test_game_state.py::TestGameState::test_performance -v
```

### Code Quality Issues

**Automatically fix:**
```bash
black .
ruff check --fix .
isort .
```

**Manual fixes:**
- Review Ruff output carefully
- Check MyPy error messages
- Ensure all functions have docstrings
- Add type hints where possible

---

## Summary

This development guide ensures consistent, high-quality code through:
- Automated formatting and linting
- Comprehensive testing with coverage reporting
- CI/CD pipeline for quality assurance
- Clear development workflows and guidelines

Following these practices will help maintain code quality and make the development process smoother for all contributors.
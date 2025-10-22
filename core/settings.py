"""
Game settings and configuration.
Framework-agnostic settings management.
"""

from dataclasses import dataclass
from typing import Dict, Any
import json
from pathlib import Path


@dataclass
class GameSettings:
    """
    Game configuration settings.
    Contains values that can be adjusted by players or for debugging.
    """
    
    # Movement settings
    movement_frequency: float = 4.0  # Movements per second
    
    # Input settings
    enable_continuous_movement: bool = True
    movement_buffer_duration: float = 0.08  # Seconds to buffer key presses for diagonal movement
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for serialization."""
        return {
            'movement_frequency': self.movement_frequency,
            'enable_continuous_movement': self.enable_continuous_movement,
            'movement_buffer_duration': self.movement_buffer_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSettings':
        """Create settings from dictionary."""
        return cls(
            movement_frequency=data.get('movement_frequency', 4.0),
            enable_continuous_movement=data.get('enable_continuous_movement', True),
            movement_buffer_duration=data.get('movement_buffer_duration', 0.08)
        )
    
    def save_to_file(self, file_path: Path) -> bool:
        """Save settings to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'GameSettings':
        """Load settings from JSON file."""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                return cls.from_dict(data)
        except Exception:
            pass
        return cls()  # Return default settings if loading fails


# Global settings instance
DEFAULT_SETTINGS = GameSettings()
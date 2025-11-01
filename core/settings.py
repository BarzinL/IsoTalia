"""Game settings and configuration management.

This module provides centralized configuration management for the IsoTalia game
engine, allowing for easy modification of game parameters and persistence of
settings across sessions.

Classes:
    GameSettings: Main configuration class for all game parameters

Example:
    >>> from core.settings import GameSettings
    >>> settings = GameSettings()
    >>> settings.movement_frequency = 5.0
    >>> settings.save_to_file(Path("settings.json"))
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import json


@dataclass
class GameSettings:
    """Game configuration settings.
    
    Contains values that can be adjusted by players or for debugging purposes.
    Settings are persisted to JSON files and can be loaded across game sessions.
    
    Attributes:
        movement_frequency (float): Number of character movements per second.
            Higher values result in faster character movement. Default is 4.0.
        enable_continuous_movement (bool): Whether to enable continuous movement
            when movement keys are held down. Default is True.
        movement_buffer_duration (float): Seconds to buffer key presses for
            diagonal movement. Prevents jittery diagonal movements. Default is 0.08.
    """
    
    # Movement settings
    movement_frequency: float = 4.0  # Movements per second
    
    # Input settings
    enable_continuous_movement: bool = True
    movement_buffer_duration: float = 0.08  # Seconds to buffer key presses for diagonal movement
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of all settings.
        """
        return {
            'movement_frequency': self.movement_frequency,
            'enable_continuous_movement': self.enable_continuous_movement,
            'movement_buffer_duration': self.movement_buffer_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GameSettings:
        """Create GameSettings from dictionary data.
        
        Args:
            data (Dict[str, Any]): Dictionary containing setting values.
            
        Returns:
            GameSettings: New GameSettings instance with values from data.
            
        Note:
            Missing keys in data will use default values.
        """
        return cls(
            movement_frequency=data.get('movement_frequency', 4.0),
            enable_continuous_movement=data.get('enable_continuous_movement', True),
            movement_buffer_duration=data.get('movement_buffer_duration', 0.08)
        )
    
    def save_to_file(self, file_path: Path) -> bool:
        """Save settings to JSON file.
        
        Args:
            file_path (Path): Path where settings file will be saved.
            
        Returns:
            bool: True if settings were saved successfully, False otherwise.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
            return True
        except Exception:
            return False
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> GameSettings:
        """Load settings from JSON file.
        
        Args:
            file_path (Path): Path to settings file to load.
            
        Returns:
            GameSettings: Settings instance with loaded values, or default
                settings if file doesn't exist or loading fails.
        """
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls.from_dict(data)
        except Exception:
            pass
        return cls()  # Return default settings if loading fails


# Global settings instance
DEFAULT_SETTINGS = GameSettings()
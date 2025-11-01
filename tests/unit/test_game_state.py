"""Unit tests for the game state management."""
import pytest
from unittest.mock import Mock, patch

from core.game_state import GameState


class TestGameState:
    """Test the GameState class."""
    
    @pytest.fixture
    def game_state(self):
        """Create a fresh game state for testing."""
        return GameState(map_width=20, map_height=20)
    
    def test_game_state_creation(self, game_state):
        """Test that GameState can be created."""
        assert game_state.map_width == 20
        assert game_state.map_height == 20
        assert game_state.tile_map is not None
        assert game_state.entity_manager is not None
        assert game_state.movement_system is not None
        assert game_state.interaction_system is not None
        assert game_state.event_bus is not None
        assert game_state.is_running is False
        assert game_state.is_paused is False
        assert game_state.game_time == 0.0
    
    def test_initialize(self, game_state):
        """Test game state initialization."""
        game_state.initialize()
        
        assert game_state.is_running is True
        assert game_state.player_entity is not None
        assert game_state.player_controller is not None
        assert game_state.game_time >= 0.0
    
    def test_generate_test_world(self, game_state):
        """Test world generation."""
        game_state.initialize()
        
        # Check that test features were added
        # Rubble at (10-14, 10)
        for x in range(10, 15):
            tile = game_state.tile_map.get_tile(x, 10)
            assert tile.tile_type.id == "rubble"
        
        # Cracked pavement in (20-29, 20-24)
        for x in range(20, 30):
            for y in range(20, 25):
                tile = game_state.tile_map.get_tile(x, y)
                assert tile.tile_type.id == "cracked_pavement"
        
        # Toxic water in (15-17, 15-17)
        for x in range(15, 18):
            for y in range(15, 18):
                tile = game_state.tile_map.get_tile(x, y)
                assert tile.tile_type.id == "toxic_water"
    
    def test_update(self, game_state):
        """Test game state updates."""
        game_state.initialize()
        initial_time = game_state.game_time
        
        game_state.update(0.5)  # 0.5 seconds
        
        assert game_state.game_time == initial_time + 0.5
    
    def test_update_paused(self, game_state):
        """Test that updates don't advance time when paused."""
        game_state.initialize()
        game_state.pause()
        
        initial_time = game_state.game_time
        game_state.update(1.0)
        
        # Time should not advance when paused
        assert game_state.game_time == initial_time
    
    def test_update_not_running(self, game_state):
        """Test that updates don't work when not running."""
        # Don't initialize - should not be running
        initial_time = game_state.game_time
        game_state.update(1.0)
        
        # Time should not advance when not running
        assert game_state.game_time == initial_time
    
    def test_process_command_move(self, game_state):
        """Test processing movement commands."""
        game_state.initialize()
        
        # Mock the movement system
        with patch.object(game_state.movement_system, 'process_movement_command') as mock_move:
            mock_move.return_value = True
            
            result = game_state.process_command('move_north')
            
            assert result is True
            mock_move.assert_called_once_with(game_state.player_entity, 'move_north')
    
    def test_process_command_dig(self, game_state):
        """Test processing dig commands."""
        game_state.initialize()
        
        # Mock the interaction system
        with patch.object(game_state.interaction_system, 'dig_adjacent') as mock_dig:
            mock_dig.return_value = {'success': True, 'drops': ['test_item']}
            
            result = game_state.process_command('dig')
            
            assert result is True
            mock_dig.assert_called_once_with(game_state.player_entity, 'north')
    
    def test_process_command_unknown(self, game_state):
        """Test processing unknown commands."""
        game_state.initialize()
        
        result = game_state.process_command('unknown_command')
        
        assert result is False
    
    def test_process_command_paused(self, game_state):
        """Test that commands don't work when paused."""
        game_state.initialize()
        game_state.pause()
        
        result = game_state.process_command('move_north')
        
        assert result is False
    
    def test_process_continuous_movement(self, game_state):
        """Test continuous movement processing."""
        game_state.initialize()
        
        with patch.object(game_state.movement_system, 'move_entity') as mock_move:
            mock_move.return_value = True
            
            result = game_state.process_continuous_movement((1, 0), 0.1)
            
            assert result is True
            mock_move.assert_called_once_with(game_state.player_entity, 1, 0)
    
    def test_process_continuous_movement_disabled(self, game_state):
        """Test that continuous movement is disabled when setting is off."""
        game_state.initialize()
        
        # Disable continuous movement
        game_state.settings.enable_continuous_movement = False
        
        with patch.object(game_state.movement_system, 'move_entity') as mock_move:
            result = game_state.process_continuous_movement((1, 0), 0.1)
            
            assert result is False
            mock_move.assert_not_called()
    
    def test_process_continuous_movement_paused(self, game_state):
        """Test that continuous movement doesn't work when paused."""
        game_state.initialize()
        game_state.pause()
        
        result = game_state.process_continuous_movement((1, 0), 0.1)
        
        assert result is False
    
    def test_process_continuous_command(self, game_state):
        """Test processing continuous commands."""
        game_state.initialize()
        
        with patch.object(game_state.movement_system, 'process_movement_command') as mock_move:
            mock_move.return_value = True
            
            result = game_state.process_continuous_command('move_east', 0.1)
            
            assert result is True
            mock_move.assert_called_once_with(game_state.player_entity, 'move_east')
    
    def test_get_render_data(self, game_state):
        """Test getting render data."""
        game_state.initialize()
        
        render_data = game_state.get_render_data(
            camera_x=0, 
            camera_y=0, 
            view_width=20, 
            view_height=20
        )
        
        assert 'tiles' in render_data
        assert 'entities' in render_data
        assert 'camera' in render_data
        assert 'game_time' in render_data
        
        assert render_data['camera']['x'] == 0
        assert render_data['camera']['y'] == 0
        assert render_data['game_time'] >= 0
    
    def test_pause(self, game_state):
        """Test pausing the game."""
        game_state.initialize()
        
        game_state.pause()
        
        assert game_state.is_paused is True
    
    def test_resume(self, game_state):
        """Test resuming the game."""
        game_state.initialize()
        game_state.pause()
        
        game_state.resume()
        
        assert game_state.is_paused is False
    
    def test_shutdown(self, game_state):
        """Test shutting down the game state."""
        game_state.initialize()
        
        game_state.shutdown()
        
        assert game_state.is_running is False
        assert len(game_state.entity_manager.get_all_entities()) == 0
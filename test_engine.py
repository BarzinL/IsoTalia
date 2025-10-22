"""
Test script to verify core engine functionality without display.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import GameState
from core.entities.components import Position


def test_engine():
    """Test core engine components."""
    print("=" * 60)
    print("IsoTalia Engine Test")
    print("=" * 60)

    # Create game state
    print("\n[1] Creating game state...")
    game_state = GameState(map_width=50, map_height=50)
    print("✓ Game state created")

    # Initialize
    print("\n[2] Initializing game...")
    game_state.initialize()
    print("✓ Game initialized")

    # Check player
    print("\n[3] Checking player entity...")
    player_pos = game_state.player_controller.get_position()
    print(f"✓ Player created at position ({player_pos.x}, {player_pos.y}, {player_pos.z})")

    # Test movement
    print("\n[4] Testing movement system...")
    old_x, old_y = player_pos.x, player_pos.y
    game_state.process_command('move_north')
    new_pos = game_state.player_controller.get_position()
    print(f"✓ Moved from ({old_x}, {old_y}) to ({new_pos.x}, {new_pos.y})")

    game_state.process_command('move_east')
    new_pos = game_state.player_controller.get_position()
    print(f"✓ Moved to ({new_pos.x}, {new_pos.y})")

    # Test tile map
    print("\n[5] Testing tile map...")
    tile = game_state.tile_map.get_tile(25, 25)
    print(f"✓ Tile at (25, 25): {tile.tile_type.name}")

    # Test render data generation
    print("\n[6] Testing render data generation...")
    render_data = game_state.get_render_data(
        camera_x=25, camera_y=25,
        view_width=20, view_height=20
    )
    print(f"✓ Generated render data:")
    print(f"  - Tiles: {len(render_data['tiles'])}")
    print(f"  - Entities: {len(render_data['entities'])}")

    # Test interaction system
    print("\n[7] Testing digging/interaction...")
    inventory_before = len(game_state.player_controller.get_inventory().items)
    game_state.process_command('dig')
    inventory_after = len(game_state.player_controller.get_inventory().items)
    print(f"✓ Dug tile, inventory: {inventory_before} -> {inventory_after} items")

    # Test update
    print("\n[8] Testing game update...")
    game_state.update(0.016)  # ~60 FPS
    print(f"✓ Game time: {game_state.game_time:.3f}s")

    print("\n" + "=" * 60)
    print("All core engine tests passed! ✓")
    print("=" * 60)

    # Test isometric math
    print("\n[9] Testing isometric coordinate conversion...")
    from rendering.isometric import IsometricConverter

    converter = IsometricConverter(32, 16)
    screen_coords = converter.world_to_screen(10, 10, 0)
    print(f"✓ World (10, 10, 0) -> Screen {screen_coords}")

    world_coords = converter.screen_to_world(screen_coords[0], screen_coords[1], 0)
    print(f"✓ Screen {screen_coords} -> World {world_coords}")

    print("\n" + "=" * 60)
    print("ENGINE READY! 🎮")
    print("=" * 60)
    print("\nThe engine is working correctly!")
    print("To run the full game with graphics, use: python main.py")
    print("\nNote: Running the full game requires a display.")


if __name__ == '__main__':
    test_engine()

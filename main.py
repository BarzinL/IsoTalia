"""
IsoTalia - Main game loop and entry point.
Integrates core engine with PyGame rendering.
"""

import pygame
import sys
from pathlib import Path

# Add core and rendering to path
sys.path.insert(0, str(Path(__file__).parent))

from core import GameState
from rendering import PyGameRenderer
from core.entities.components import Position


class InputHandler:
    """
    Handles PyGame input and converts to framework-agnostic commands.
    """

    def __init__(self):
        # Key mapping to game commands
        self.key_map = {
            pygame.K_w: 'move_north',
            pygame.K_UP: 'move_north',
            pygame.K_s: 'move_south',
            pygame.K_DOWN: 'move_south',
            pygame.K_a: 'move_west',
            pygame.K_LEFT: 'move_west',
            pygame.K_d: 'move_east',
            pygame.K_RIGHT: 'move_east',
            pygame.K_SPACE: 'dig',
            pygame.K_e: 'interact',
        }

        # Held keys for continuous movement
        self.held_keys = set()

    def process_event(self, event: pygame.event.Event) -> list:
        """
        Process a PyGame event and return list of game commands.
        """
        commands = []

        if event.type == pygame.KEYDOWN:
            self.held_keys.add(event.key)

            # Map to game command
            if event.key in self.key_map:
                commands.append(self.key_map[event.key])

            # Special commands
            if event.key == pygame.K_F3:
                commands.append('toggle_debug')
            elif event.key == pygame.K_ESCAPE:
                commands.append('quit')

        elif event.type == pygame.KEYUP:
            if event.key in self.held_keys:
                self.held_keys.remove(event.key)

        return commands


class Game:
    """
    Main game class that integrates everything.
    """

    def __init__(self):
        # Core game state
        self.game_state = GameState(map_width=50, map_height=50)

        # Rendering
        self.renderer = PyGameRenderer(
            screen_width=1280,
            screen_height=720,
            tile_width=32,
            tile_height=16
        )

        # Input handling
        self.input_handler = InputHandler()

        # Game loop control
        self.running = False
        self.clock = pygame.time.Clock()
        self.target_fps = 60

    def initialize(self):
        """Initialize the game."""
        self.game_state.initialize()

        # Center camera on player
        player_pos = self.game_state.player_controller.get_position()
        if player_pos:
            self.renderer.center_camera_on(player_pos.x, player_pos.y)

        self.running = True

    def handle_input(self):
        """Handle input events."""
        # Process all pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Get game commands from event
            commands = self.input_handler.process_event(event)

            for command in commands:
                self._process_command(command)

    def _process_command(self, command: str):
        """Process a game command."""
        if command == 'quit':
            self.running = False
        elif command == 'toggle_debug':
            self.renderer.toggle_debug()
        else:
            # Pass to game state
            self.game_state.process_command(command)

    def update(self, delta_time: float):
        """Update game state."""
        self.game_state.update(delta_time)

        # Update camera to follow player
        player_pos = self.game_state.player_controller.get_position()
        if player_pos:
            self.renderer.center_camera_on(player_pos.x, player_pos.y)

    def render(self):
        """Render the frame."""
        # Get render data from game state
        # Calculate visible bounds for culling
        min_x, min_y, max_x, max_y = self.renderer.camera.get_visible_bounds()
        view_width = max_x - min_x
        view_height = max_y - min_y

        render_data = self.game_state.get_render_data(
            camera_x=min_x,
            camera_y=min_y,
            view_width=view_width,
            view_height=view_height
        )

        # Render
        self.renderer.render(render_data)

    def run(self):
        """Main game loop."""
        self.initialize()

        while self.running:
            # Calculate delta time
            delta_time = self.clock.tick(self.target_fps) / 1000.0  # Convert to seconds

            # Game loop
            self.handle_input()
            self.update(delta_time)
            self.render()

        self.shutdown()

    def shutdown(self):
        """Clean shutdown."""
        self.game_state.shutdown()
        self.renderer.shutdown()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()

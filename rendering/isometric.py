"""
Isometric coordinate conversion utilities.
Handles conversion between world coordinates and screen coordinates.
"""

from typing import Tuple


class IsometricConverter:
    """
    Handles coordinate conversions for isometric projection.
    Uses diamond/staggered layout with 32x16 pixel tiles.
    """

    def __init__(self, tile_width: int = 32, tile_height: int = 16):
        """
        Initialize converter with tile dimensions.
        For diamond isometric: width should be 2x height (e.g., 32x16, 64x32)
        """
        self.tile_width = tile_width
        self.tile_height = tile_height

    def world_to_screen(self, world_x: int, world_y: int, world_z: int = 0) -> Tuple[int, int]:
        """
        Convert world (grid) coordinates to screen (pixel) coordinates.

        Args:
            world_x: Grid X coordinate
            world_y: Grid Y coordinate
            world_z: Grid Z coordinate (elevation)

        Returns:
            (screen_x, screen_y) tuple in pixels
        """
        # Standard isometric transformation
        screen_x = (world_x - world_y) * (self.tile_width // 2)
        screen_y = (world_x + world_y) * (self.tile_height // 2)

        # Apply Z offset (elevation raises tiles visually)
        screen_y -= world_z * (self.tile_height // 2)

        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: int, screen_y: int, world_z: int = 0) -> Tuple[int, int]:
        """
        Convert screen (pixel) coordinates to world (grid) coordinates.

        Args:
            screen_x: Screen X coordinate in pixels
            screen_y: Screen Y coordinate in pixels
            world_z: Assumed Z level (for accurate conversion)

        Returns:
            (world_x, world_y) tuple
        """
        # Adjust for Z offset
        adjusted_y = screen_y + world_z * (self.tile_height // 2)

        # Inverse isometric transformation
        world_x = (screen_x / (self.tile_width // 2) + adjusted_y / (self.tile_height // 2)) / 2
        world_y = (adjusted_y / (self.tile_height // 2) - screen_x / (self.tile_width // 2)) / 2

        # Round to nearest grid position
        return (int(round(world_x)), int(round(world_y)))

    def get_tile_screen_rect(self, world_x: int, world_y: int, world_z: int = 0) -> Tuple[int, int, int, int]:
        """
        Get the screen rectangle for a tile (for rendering).

        Returns:
            (x, y, width, height) tuple
        """
        screen_x, screen_y = self.world_to_screen(world_x, world_y, world_z)

        # Center the tile on the calculated position
        x = screen_x - self.tile_width // 2
        y = screen_y - self.tile_height // 2

        return (x, y, self.tile_width, self.tile_height)

    def get_depth_sort_key(self, world_x: int, world_y: int, world_z: int, layer: int = 0) -> int:
        """
        Get sorting key for depth sorting (painter's algorithm).
        Higher values are drawn later (on top).

        Args:
            world_x: Grid X
            world_y: Grid Y
            world_z: Grid Z (elevation)
            layer: Render layer (0=ground, 1=entities, 2=effects)

        Returns:
            Sort key integer
        """
        # Sort by: Y (back to front), X (left to right), Z (bottom to top), then layer
        # Multiply by large values to ensure proper ordering
        return (world_y * 1000000) + (world_x * 10000) + (world_z * 100) + layer


class Camera:
    """
    Camera system for viewport management.
    Tracks camera position in world space.
    """

    def __init__(self, screen_width: int, screen_height: int,
                 tile_width: int = 32, tile_height: int = 16):
        """
        Initialize camera.

        Args:
            screen_width: Screen width in pixels
            screen_height: Screen height in pixels
            tile_width: Tile width for calculations
            tile_height: Tile height for calculations
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Camera position in world coordinates (can be floating point)
        self.x = 0.0
        self.y = 0.0

        # Offset in pixels (for smooth scrolling)
        self.offset_x = 0
        self.offset_y = 0

    def center_on(self, world_x: int, world_y: int):
        """Center camera on world position."""
        self.x = world_x
        self.y = world_y

    def move(self, dx: float, dy: float):
        """Move camera by delta."""
        self.x += dx
        self.y += dy

    def world_to_screen_with_camera(self, world_x: int, world_y: int, world_z: int = 0,
                                    converter: IsometricConverter = None) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates accounting for camera position.

        Args:
            world_x: World X
            world_y: World Y
            world_z: World Z
            converter: IsometricConverter instance

        Returns:
            (screen_x, screen_y) tuple
        """
        if converter is None:
            converter = IsometricConverter(self.tile_width, self.tile_height)

        # Get base screen position
        screen_x, screen_y = converter.world_to_screen(world_x, world_y, world_z)

        # Apply camera offset
        cam_screen_x, cam_screen_y = converter.world_to_screen(int(self.x), int(self.y), 0)

        # Center on screen
        final_x = screen_x - cam_screen_x + self.screen_width // 2 + self.offset_x
        final_y = screen_y - cam_screen_y + self.screen_height // 2 + self.offset_y

        return (final_x, final_y)

    def get_visible_bounds(self) -> Tuple[int, int, int, int]:
        """
        Get world bounds of visible area for isometric projection.
        Returns (min_x, min_y, max_x, max_y) with proper padding.
        """
        # Create a converter for calculations
        converter = IsometricConverter(self.tile_width, self.tile_height)
        
        # Get camera center position in screen coordinates
        cam_screen_x, cam_screen_y = converter.world_to_screen(int(self.x), int(self.y), 0)
        
        # Calculate screen corners relative to camera center
        screen_corners = [
            (-self.screen_width // 2, -self.screen_height // 2),  # Top-left
            (self.screen_width // 2, -self.screen_height // 2),   # Top-right
            (self.screen_width // 2, self.screen_height // 2),    # Bottom-right
            (-self.screen_width // 2, self.screen_height // 2)    # Bottom-left
        ]
        
        # Convert screen corners to world coordinates
        world_coords = []
        for corner_x, corner_y in screen_corners:
            # Adjust for camera position
            screen_x = cam_screen_x + corner_x
            screen_y = cam_screen_y + corner_y
            
            # Convert to world coordinates
            world_x, world_y = converter.screen_to_world(screen_x, screen_y, 0)
            world_coords.append((world_x, world_y))
        
        # Find bounds with padding
        padding = 2  # Add some padding to ensure edge tiles are included
        min_x = min(coord[0] for coord in world_coords) - padding
        max_x = max(coord[0] for coord in world_coords) + padding
        min_y = min(coord[1] for coord in world_coords) - padding
        max_y = max(coord[1] for coord in world_coords) + padding
        
        return (min_x, min_y, max_x, max_y)

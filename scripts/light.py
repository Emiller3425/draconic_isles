import pygame

# TODO Add size input parameter
class Light:
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos

        # self.size = size

        # Create a light mask with a gradient (100x100 size for a 50-pixel radius light)
        self.light_mask = pygame.Surface((100, 100), pygame.SRCALPHA)
        
        # Draw a radial gradient circle on the light mask
        for r in range(50, 0, -1):
            alpha = int(255 * (1 - r / 50))  # Calculate alpha value (0 at center to 255 at edge)
            pygame.draw.circle(self.light_mask, (0, 0, 0, alpha), (50, 50), r)

    def render(self, overlay, offset=(0, 0)):
    
        if self.game.weather_system.night_overlay_opacity > 0:
            # Correctly calculate the position to blit the light mask, centered on the lantern
            lantern_x = self.pos[0] - offset[0] - 42  # Adjust by half the light mask width
            lantern_y = self.pos[1] - offset[1] - 42  # Adjust by half the light mask height
            overlay.blit(self.light_mask, (lantern_x, lantern_y), special_flags=pygame.BLEND_RGBA_SUB)

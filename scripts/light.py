import pygame

# TODO Add size input parameter
class Light:
    def __init__(self, game, pos, size, color):
        self.game = game
        self.pos = pos
        self.size = size
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]

        # self.size = size

        # Create a light mask with a gradient (100x100 size for a 50-pixel radius light)
        self.light_mask = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Draw a radial gradient circle on the light mask
        for r in range(self.size, 0, -1):
            alpha = int(255 * (1 - r / self.size))
            if alpha < 0:  # Calculate alpha value (0 at center to 255 at edge)
                alpha *= - 1
            pygame.draw.circle(self.light_mask, (self.red, self.green, self.blue, alpha), (self.size, self.size), r)

    def render(self, overlay, offset=(0, 0)):
    
        if self.game.weather_system.night_overlay_opacity > 0:
            # Correctly calculate the position to blit the light mask, centered on the lantern
            light_x= self.pos[0] - offset[0] - self.size + 8 # Adjust by half the light mask width
            light_y = self.pos[1] - offset[1] - self.size + 8 # Adjust by half the light mask height
            overlay.blit(self.light_mask, (light_x, light_y), special_flags=pygame.BLEND_RGBA_SUB)
            overlay.blit(self.light_mask, (light_x, light_y), special_flags=pygame.BLEND_RGB_ADD)

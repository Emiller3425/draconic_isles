import pygame

DECORATIVE_TYPES = {
    'bush',
}

# Work in progress may have to change all of this
class Decorative:
    def __init__(self, game, d_type, pos, frame=0):
        self.game = game
        self.type = d_type
        self.pos = list(pos)
        self.animation = self.game.assets[d_type]  # Use the correct asset for the decorative type
        self.animation_frame = frame

    def update(self):
        # Update the animation frame
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # Render the current frame of the animation
        img = self.animation.img()
        surf.blit(
            img, 
            (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2)
        )
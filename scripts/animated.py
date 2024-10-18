import pygame
import random

class Animated:
    def __init__(self, game, type, pos, frame):
        self.game = game
        self.pos = pos
        self.anim_offset = (0,0)
        self.flip = False
        self.type = type
        self.animation = self.game.assets[self.type + '/animation'].copy()  # Load the bonfire animation
        # Randomize starting frame for certain animated objects
        self.frame = frame
        # Start the animation at the randomized frame
        self.animation.frame = self.frame * self.animation.img_duration
            

    def update(self):
        self.animation.update()  # Update the animation each frame

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))
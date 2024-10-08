import pygame
import math
import random

# TODO The bonfire class is used to create a bonfire which acts as a save point for the player when they die, 
# players can interact with to set spawn and can also fast travel in between,
# May introduce upgrade system later with this
class Bonfire:
    def __init__(self, game, pos):
        self.game = game
        self.pos = pos
        self.anim_offset = (0,0)
        self.flip = False
        self.animation = self.game.assets['bonfire/animation'].copy()  # Load the bonfire animation

    def update(self):
        self.animation.update()  # Update the animation each frame

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))
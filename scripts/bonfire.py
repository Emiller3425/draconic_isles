import pygame
import math
import random
import json

from scripts.light import Light

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
        self.game.lights.append(Light(self.game, (pos[0] + 8, pos[1] + 8), 50, [50, 20, 0]))

    def update(self):
        self.animation.update()  # Update the animation each frame

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))
        
    def render_interact(self, surf, offset=(0,0)):
        surf.blit(pygame.transform.flip(self.game.assets['f_key'].copy(), self.flip, False), 
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                self.pos[1] - offset[1] + self.anim_offset[1]))
        
    def save_game(self, ):
        pass
        


import pygame
import math
import random
import json

from scripts.light import Light
from scripts.drop import Drop
from scripts.drop import Souls


# TODO enable chests to drop items
class Chest:
    def __init__(self, game, pos, type):
        self.game = game
        self.pos = pos
        self.anim_offset = (0, 0)
        self.flip = False
        self.is_opened = False
        self.drops = []
        if type == 0:
            self.animation = self.game.assets['bronze_chest_animation'].copy()
        elif type == 1:
            self.animation = self.game.assets['silver_chest_animation'].copy()
        else:
            self.animation = self.game.assets['gold_chest_animation'].copy()

        # holds data of all potential drops in the game, TODO may need to add image field to hold the image of the item whend ropped
        self.potential_drops = {
            {'weapons' : {
                'basic_sword' : {'damage' : 10, 'cooldown' : 30, 'stamina_cost' : 10,}
            }},
            {'spells' : {
                'fireball' : {'damage' : 20, 'mana_cost' : 10, 'velocity': 2, 'restoration' : 0},
                'lightning' : {'damage' : 30, 'mana_cost' : 25, 'velocity': 40, 'restoration' : 0},
            }}
        }

    def drop_items(self):
        print('drop')
        self.game.drops.append(Souls(self.game, 'soul', (self.pos[0], self.pos[1] + 8), 1000))

    def select_drops(self):
        pass

    def update(self):
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                self.pos[1] - offset[1] + self.anim_offset[1]))
        
    def render_interact(self, surf, offset=(0,0)):
        if not self.is_opened:
            offset = (offset[0], offset[1] + 18)
            surf.blit(pygame.transform.flip(self.game.assets['f_key'].copy(), self.flip, False), 
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                self.pos[1] - offset[1] + self.anim_offset[1]))

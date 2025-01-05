import pygame
import time
import json
import random

from scripts.weapon import Weapon
from scripts.spell import Spell

class Drop:
    def __init__(self, game, pos, drop_name, image = None, tile_size = 16):
        self.game = game
        self.pos = (pos[0] + 8, pos[1] + 8)
        self.center = self.pos
        self.original_pos = self.pos
        self.top_pos = (self.pos[0], self.pos[1] - 2)
        self.bottom_pos = (self.pos[0], self.pos[1] + 2)
        self.movement = 'up'
        self.drop_name = drop_name
        self.image = image # set to whatever the drop image is
        self.tile_size = tile_size
        self.has_particle_spawner = False
        self.spawner = None
        self.potential_drops = {
            'weapons' : {
                'basic_sword' : {'damage' : random.randint(5,10), 'cooldown' : 30, 'stamina_cost' : 10,},
                'heavy_sword' : {'damage' : random.randint(12,18), 'cooldown' : 30, 'stamina_cost' : 10,},
            },
            'spells' : {
                'fireball' : {'damage' : random.randint(10,20), 'mana_cost' : 10, 'velocity': 2, 'restoration' : 0},
                'lightning' : {'damage' : random.randint(25, 35), 'mana_cost' : 25, 'velocity': 40, 'restoration' : 0},
            }
        }
        
        # TODO pass stats from item to thing
        if self.drop_name in self.potential_drops['weapons']:
            self.item = Weapon(self.game, self.drop_name, self.potential_drops['weapons'][self.drop_name]['damage'], self.potential_drops['weapons'][self.drop_name]['cooldown'], self.potential_drops['weapons'][self.drop_name]['stamina_cost'])
        elif self.drop_name in self.potential_drops['spells']:
             self.item = Spell(self.game, self.drop_name, self.potential_drops['spells'][self.drop_name]['damage'], self.potential_drops['spells'][self.drop_name]['mana_cost'], self.potential_drops['spells'][self.drop_name]['velocity'], self.potential_drops['spells'][self.drop_name]['restoration'])

    def update(self):
        if self.movement == 'up':
            if self.pos[1] > self.top_pos[1]:
                self.pos = (self.pos[0], self.pos[1] - 0.075)
            else:
                self.movement = 'down'
        else:
            if self.pos[1] < self.bottom_pos[1]:
                self.pos = (self.pos[0], self.pos[1] + 0.075)
            else:
                self.movement = 'up'
        
        self.player_pickup()

    def player_pickup(self):
        self.distance = [
            (self.center[0] - self.game.player.pos[0]) // self.tile_size, 
            (self.center[1] - self.game.player.pos[1]) // self.tile_size
                            ] 
        if (self.distance[0] > -1 and self.distance[0] < 1 and self.distance[1] > -1 and self.distance[1] < 1):
            if self.item.__class__ == Weapon:
                self.game.player.weapon_inventory.append(self.item)
                self.game.drops.remove(self)
            else:
                self.game.player.spell_inventory.append(self.item)
                self.game.drops.remove(self)

    def render(self, surf, offset = (0, 0)):
        img = self.image
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

class Souls(Drop):
    def __init__(self, game, pos, drop_name, image, souls):
        super().__init__(game, pos, drop_name, image)
        self.souls = souls

    def update(self):
        super().update()

    def player_pickup(self):
        self.distance = [
            (self.center[0] - self.game.player.pos[0]) // self.tile_size, 
            (self.center[1] - self.game.player.pos[1]) // self.tile_size
                            ] 
        
        if (self.distance[0] > -1 and self.distance[0] < 1 and self.distance[1] > -1 and self.distance[1] < 1) and (self.spawner, self.__class__) in self.game.drop_particle_spawners:
            self.game.player.souls += self.souls
            self.game.drops.remove(self)
            self.game.drop_particle_spawners.remove((self.spawner, self.__class__))
        
    def render(self, surf, offset = (0,0)):
        super().render(surf, offset)

import pygame
import time
import json

class Drop:
    def __init__(self, game, type, pos, tile_size = 16):
        self.game = game
        self.type = type
        self.pos = (pos[0] + 8, pos[1] + 8)
        self.center = self.pos
        self.original_pos = self.pos
        self.top_pos = (self.pos[0], self.pos[1] - 2)
        self.bottom_pos = (self.pos[0], self.pos[1] + 2)
        self.movement = 'up'
        self.image = None  # set to whatever the drop image is
        self.tile_size = tile_size
        self.has_particle_spawner = False
        self.spawner = None

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

    def player_pickup(self):
        self.distance = [
            (self.center[0] - self.game.player.pos[0]) // self.tile_size, 
            (self.center[1] - self.game.player.pos[1]) // self.tile_size
                            ] 
        # self.distance[0] = abs(self.distance[0])
        # self.distance[1] = abs(self.distance[1])


    def render(self, surf, offset = (0, 0)):
        img = self.image
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

class Souls(Drop):
    def __init__(self, game, type, pos, souls):
        super().__init__(game, type, pos)
        self.image = self.game.assets['dropped_souls']
        self.souls = souls

    def update(self):
        super().update()
        self.player_pickup()

    def player_pickup(self):
        super().player_pickup()

        if (self.distance[0] > -1 and self.distance[0] < 1 and self.distance[1] > -1 and self.distance[1] < 1) and self.spawner in self.game.drop_particle_spawners:
            self.game.player.souls += self.souls
            self.game.drops.remove(self)
            self.game.drop_particle_spawners.remove(self.spawner)
        
    def render(self, surf, offset = (0,0)):
        super().render(surf, offset)

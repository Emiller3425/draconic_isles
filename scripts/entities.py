import pygame
import random
import asyncio
import sys
from scripts.tilemap import Tilemap


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity_x = [0, 0]
        self.velocity_y = [0, 0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.is_facing = 'down'
        self.set_action('idle_down')

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        # Process horizontal movement first
        if movement_x[0]:  # Moving left
            self.pos[0] -= 1
            self.handle_collisions('left')
            self.is_facing = 'left'
            # self.set_action('walking_horizontal')
        if movement_x[1]:  # Moving right
            self.pos[0] += 1
            self.handle_collisions('right')
            self.is_facing = 'right'
            # self.set_action('walking_horizontal')
        # Then process vertical movement
        if movement_y[0]:  # Moving up
            self.pos[1] -= 1
            self.handle_collisions('up')
            self.is_facing = 'up'
            # self.set_action('walking_vertical')
        if movement_y[1]:  # Moving down
            self.pos[1] += 1
            self.handle_collisions('down')
            self.is_facing = 'down'
            self.set_action('walking')
        
        if movement_x[0] == 0 and movement_x[1] == 0 and movement_y[0] == 0 and movement_y[1] == 0:
            if self.is_facing == 'down':
                self.set_action('idle_down')
            elif self.is_facing == 'up':
                self.set_action('idle_up')
        
        self.animation.update()
        
    def handle_collisions(self, direction):
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos, self.size):
            if entity_rect.colliderect(rect):
                if direction == 'left':
                    self.collisions['left'] = True
                    self.pos[0] = rect.right  # Adjust position to prevent overlap
                elif direction == 'right':
                    self.collisions['right'] = True
                    self.pos[0] = rect.left - self.size[0]  # Adjust position to prevent overlap
                elif direction == 'up':
                    self.collisions['up'] = True
                    self.pos[1] = rect.bottom  # Adjust position to prevent overlap
                elif direction == 'down':
                    self.collisions['down'] = True
                    self.pos[1] = rect.top - self.size[1]  # Adjust position to prevent overlap

    def render(self, surf, offset=(0, 0)):
        # Draw the entity
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))


# Class for the player character, inherits from PhysicsEntity
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)

        self.image = self.game.assets['player']


    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        super().update(movement_x, movement_y)  # Update position based on movement

    # Override the render method and add custom offset for player sprite
    def render(self, surf, offset=(0, 0)):
        # Draw the hitbox (rectangle) first
        hitbox_color = (255, 0, 0)  # Red color for the hitbox (you can change this to any color you like)
        pygame.draw.rect(
            surf, 
            hitbox_color, 
            (self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1]), 
            1  # Width of 1 for the rectangle border
        )

        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0],
                   self.pos[1] - offset[1] + self.anim_offset[1]-4))
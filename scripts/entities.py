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

        # Process vertical movement first
        if movement_y[0]:  # Moving up
            self.pos[1] -= movement_y[0]
            self.handle_collisions('up')
            self.is_facing = 'up'
            self.flip = False
            if movement_x[0] != 1 and movement_x[1] != 1:
                self.set_action('walking_up')
        if movement_y[1]:  # Moving down
            self.pos[1] += movement_y[1]
            self.handle_collisions('down')
            self.is_facing = 'down'
            self.flip = False
            if movement_x[0] != 1 and movement_x[1] != 1:
                self.set_action('walking_down')
                
        # Process horizontal movement second
        if movement_x[0]:  # Moving left
            self.pos[0] -= movement_x[0]
            self.handle_collisions('left')
            self.is_facing = 'left'
            self.flip = True
            self.set_action('walking_horizontal')
        if movement_x[1]:  # Moving right
            self.pos[0] += movement_x[1]
            self.handle_collisions('right')
            self.is_facing = 'right'
            self.flip = False
            self.set_action('walking_horizontal')
        
        if movement_x[0] == False and movement_x[1] == False and movement_y[0] == False and movement_y[1] == False:
            if self.is_facing == 'down':
                self.set_action('idle_down')
            elif self.is_facing == 'up':
                self.set_action('idle_up')
            elif self.is_facing == 'left' or self.is_facing == 'right':
                self.set_action('idle_horizontal')
        
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
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.mana = 100
        self.max_mana = 100
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
                   self.pos[1] - offset[1] + self.anim_offset[1]-6))
        
class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'skeleton', pos, size)
        self.health = 25
        self.max_health = 25
        self.stamina = 25
        self.max_stamina = 25
        self.mana = 25
        self.max_mana = 25
        self.image = self.game.assets['skeleton']

    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        super().update(movement_x, movement_y)

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
                   self.pos[1] - offset[1] + self.anim_offset[1]-6))
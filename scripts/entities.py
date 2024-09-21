import pygame
import random
import asyncio
import sys
from scripts.tilemap import Tilemap
from scripts.projectile import Projectile, FireballSpell


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

    def die(self):
        # Because each entity type is in a different data structure, we need to handle this in the child class
        pass
    
    def melee(self):
        # Melee attack
        self.melee_attack = True
        if self.is_facing == 'up':
            #self.set_action('melee_up')
            self.melee_hitbox = pygame.Rect(self.pos[0]+4, self.pos[1] - 14, 8, 18)
        elif self.is_facing == 'down':
            #self.set_action('melee_down')
            self.melee_hitbox = pygame.Rect(self.pos[0]+4, self.pos[1] + 4, 8, 18)
        elif self.is_facing == 'left':
            self.melee_hitbox = pygame.Rect(self.pos[0]-14, self.pos[1], 18, 8)
            #self.set_action('melee_horizontal')
        elif self.is_facing == 'right':
            self.melee_hitbox = pygame.Rect(self.pos[0]+12, self.pos[1], 18, 8)
            #self.set_action('melee_horizontal')
        if self.melee_attack == True:
            self.can_attack = True
            
        
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
        self.melee_hitbox = None
        self.image = self.game.assets['player']
        self.equipped_melee = 'basic_sword'
        self.equipped_spell = 'fireball'
        self.spell_velocity = [0, 0]  # Default spell velocity, down because that is the default player facing direciton
        self.is_facing = 'down'
        self.vertical_spell = False
        self.vertical_spell_flip = False

        self.attack_cooldowns = {
            'melee': {'current': 0, 'max': 60},  # Example: Melee attack has a 60-frame cooldown
        }

        self.spell_details = {
            'fireball': {'mana_cost': 10, 'velocity': 2},  # Fireball costs 10 mana
            # Add additional spells and their costs here
        }

        # Stamina recovery management
        self.stamina_recovery_start = None  # To track when stamina recovery can begin
        self.stamina_regen_cooldown = 2000  # 2 seconds in milliseconds
        self.stamina_regen_rate = 1  # Regenerate 1 stamina per tick

        # Mana recovery management
        self.mana_recovery_start = None  # To track when mana recovery can begin
        self.mana_regen_cooldown = 2000  # 2 seconds in milliseconds
        self.mana_regen_rate = 0.02  # Regenerate 1 mana per tick

    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        super().update(movement_x, movement_y)  # Update position based on movement

        # Decrease the cooldowns
        for attack in self.attack_cooldowns:
            if self.attack_cooldowns[attack]['current'] > 0:
                self.attack_cooldowns[attack]['current'] -= 1

        # Check for stamina regeneration after 3 seconds
        if self.stamina < self.max_stamina and self.stamina_recovery_start:
            time_since_last_melee = pygame.time.get_ticks() - self.stamina_recovery_start
            if time_since_last_melee >= self.stamina_regen_cooldown:
                self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate)  # Regenerate 1 stamina per tick

        # Mana regeneration logic
        if self.mana < self.max_mana and self.mana_recovery_start:
            time_since_last_spell = pygame.time.get_ticks() - self.mana_recovery_start
            if time_since_last_spell >= self.mana_regen_cooldown:
                self.mana = min(self.max_mana, self.mana + self.mana_regen_rate)  # Regenerate mana per tick

        if self.health <= 0:
            self.die()

    def die(self):
        # TODO Implement player death
        pass

    def melee(self):
        # Check if the melee attack cooldown is finished and if enough stamina is available
        if self.attack_cooldowns['melee']['current'] == 0 and self.stamina >= 15:
            super().melee()

            # Reduce stamina by 15
            self.stamina -= 15
            self.stamina_recovery_start = pygame.time.get_ticks()  # Start the recovery timer

            # Check for collision with enemies
            for enemy in self.game.enemies:
                if self.melee_hitbox and self.melee_hitbox.colliderect(enemy.rect()):
                    enemy.health -= 10

            # Start the cooldown timer after performing a melee attack
            self.attack_cooldowns['melee']['current'] = self.attack_cooldowns['melee']['max']

    def cast_spell(self):
        # Check if the player has enough mana to cast the equipped spell
        if self.mana >= self.spell_details[self.equipped_spell]['mana_cost']:
            if self.is_facing == 'up':
                self.spell_velocity = [0, -self.spell_details[self.equipped_spell]['velocity']]
                self.vertical_spell = True
                self.vertical_spell_flip = True
            if self.is_facing == 'down':
                self.spell_velocity = [0, self.spell_details[self.equipped_spell]['velocity']]
                self.vertical_spell = True
                self.vertical_spell_flip = False
            if self.is_facing == 'left':
                self.spell_velocity = [-self.spell_details[self.equipped_spell]['velocity'], 0]
                self.vertical_spell = False
                self.vertical_spell_flip = False
            if self.is_facing == 'right':
                self.spell_velocity = [self.spell_details[self.equipped_spell]['velocity'], 0]
                self.vertical_spell = False
                self.vertical_spell_flip = False
            if self.equipped_spell == 'fireball':
                # Create a fireball projectile and add it to the game's projectile list
                fireball = FireballSpell(self.game, self.pos, self.spell_velocity, self.vertical_spell, self.vertical_spell_flip)
                self.game.projectiles.append(fireball)

            # Deduct mana for casting the spell
            self.mana -= self.spell_details[self.equipped_spell]['mana_cost']

            # Start mana recovery timer
            self.mana_recovery_start = pygame.time.get_ticks()

        else:
            print("Not enough mana to cast the spell.")

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
                   self.pos[1] - offset[1] + self.anim_offset[1] - 6))
        
        # Render melee hitbox
        if self.melee_hitbox is not None:
            melee_hitbox_color = (0, 255, 0)  # Green color for the melee hitbox
            pygame.draw.rect(surf, melee_hitbox_color, 
                             pygame.Rect(self.melee_hitbox.x - offset[0], 
                                         self.melee_hitbox.y - offset[1], 
                                         self.melee_hitbox.width, 
                                         self.melee_hitbox.height), 1)
   
        
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
        if self.health <= 0:
            self.die()

    def die(self):
        self.game.enemies.remove(self)
    
    def melee(self):
        # TODO Implement enemy melee attack
        super().melee(1, 1)
        if self.game.player.rect().colliderect(self.melee_hitbox):
            self.game.player.health -= 10

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
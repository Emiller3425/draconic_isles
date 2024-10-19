import pygame
import random
import asyncio
import sys
import json
import numpy as np

from scripts.drop import Drop, Souls
from scripts.tilemap import Tilemap
from scripts.projectile import Projectile, FireballSpell


class PhysicsEntity:
    def __init__(self, game, e_type, pos, damage_hitbox, physics_hitbox):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.damage_hitbox = damage_hitbox
        self.damage_offset_y = (16 - damage_hitbox[1]) / 2
        self.damage_offset_x = (16 - damage_hitbox[0]) / 2
        self.physics_hitbox = physics_hitbox
        self.physics_offset_y = (16 - physics_hitbox[1]) / 2
        self.physics_offset_x = (16 - physics_hitbox[0]) / 2
        self.velocity_x = [0, 0]
        self.velocity_y = [0, 0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.is_facing = 'down'
        self.souls = 0
        self.set_action('idle_down')
    
    def damage_rect(self):
        return pygame.Rect(self.pos[0] + self.damage_offset_x, self.pos[1] + self.damage_offset_y, self.damage_hitbox[0], self.damage_hitbox[1])
    
    def physics_rect(self):
        return pygame.Rect(self.pos[0] + self.physics_offset_x, self.pos[1] + self.physics_offset_y, self.physics_hitbox[0], self.physics_hitbox[1])

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
        self.game.enemies.remove(self)
        self.game.player.souls += self.souls

    def melee(self):
        self.melee_attack = True
        if self.is_facing == 'up':
            self.melee_hitbox = pygame.Rect(self.pos[0] + 4, self.pos[1] - 14, 8, 18)
        elif self.is_facing == 'down':
            self.melee_hitbox = pygame.Rect(self.pos[0] + 4, self.pos[1] + 14, 8, 18)
        elif self.is_facing == 'left':
            self.melee_hitbox = pygame.Rect(self.pos[0] - 14, self.pos[1], 18, 8)
        elif self.is_facing == 'right':
            self.melee_hitbox = pygame.Rect(self.pos[0] + 12, self.pos[1], 18, 8)
        if self.melee_attack == True:
            self.can_attack = True
            
    def handle_collisions(self, direction):
        entity_rect = self.physics_rect()
        for rect in self.game.tilemap.physics_rects_around((self.pos[0] + self.physics_offset_x, self.pos[1] + self.physics_offset_y), self.physics_hitbox, 'entity'):
            if entity_rect.colliderect(rect):
                if direction == 'left':
                    self.collisions['left'] = True
                    self.pos[0] = rect.right - self.physics_offset_x
                elif direction == 'right':
                    self.collisions['right'] = True
                    self.pos[0] = rect.left - self.physics_hitbox[0] - 1
                elif direction == 'up':
                    self.collisions['up'] = True
                    self.pos[1] = rect.bottom - self.physics_offset_y
                elif direction == 'down':
                    self.collisions['down'] = True
                    self.pos[1] = rect.top - self.physics_hitbox[1] - self.physics_offset_y

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))


# Class for the player character
class Player(PhysicsEntity):
    def __init__(self, game, pos, damage_hitbox, physics_hitbox):
        super().__init__(game, 'player', pos, damage_hitbox, physics_hitbox)
        self.spawn_point = self.pos.copy()
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.mana = 100
        self.max_mana = 100
        self.souls = 0
        self.melee_hitbox = None
        self.image = self.game.assets['player']
        self.equipped_melee = 'basic_sword'
        self.equipped_spell = 'fireball'
        self.spell_velocity = [0, 0]
        self.is_facing = 'down'
        self.vertical_spell = False
        self.vertical_spell_flip = False
        self.melee_attack_duration = 0 
        self.is_melee_attacking = False
        self.nearby_bonfires = []
        self.nearby_bonfire_objects = []

        self.attack_cooldowns = {
            'melee': {'current': 0, 'max': 30},
        }

        self.spell_details = {
            'fireball': {'mana_cost': 10, 'velocity': 2},
        }

        self.stamina_recovery_start = None
        self.stamina_regen_cooldown = 2000
        self.stamina_regen_rate = 1

        self.mana_recovery_start = None
        self.mana_regen_cooldown = 2000
        self.mana_regen_rate = 0.02

        self.knockback_velocity = [0, 0]
        self.knockback_duration = 10
        self.knockback_remaining = 0
        self.knockback_direction = None

    def rest_at_bonfire(self):
        if len(self.nearby_bonfires) > 0:
            self.spawn_point = [self.nearby_bonfire_objects[0].pos[0] + 8, self.nearby_bonfire_objects[0].pos[1] + 32]
            self.health = self.max_health
            self.stamina = self.max_stamina
            self.mana = self.max_mana

            # Information to save into JSON file
            data = {
            'max_health' : self.max_health,
            'max_stamina' : self.max_stamina,
            'max_mana' : self.max_mana,
            'souls' : self.souls,
            'equipped_melee' : self.equipped_melee,
            'equipped_spell' : self.equipped_spell,
            'spawn_point' : self.spawn_point
            }

            with open('save_files/save.json', 'w') as save_file:
                json.dump(data, save_file)
    
    def update(self, movement_x=(0, 0), movement_y=(0, 0)):

        # Reset Nearby Bonfires
        self.nearby_bonfires = []
        self.nearby_bonfire_objects = []

        if self.knockback_remaining > 0:
            self.apply_knockback_movement()
        elif not self.is_melee_attacking:
            super().update(movement_x, movement_y)

        # Check For Nearby Bonfires
        self.nearby_bonfires = self.game.tilemap.bonfires_around((self.pos[0] + self.physics_offset_x, self.pos[1] + self.physics_offset_y), self.physics_hitbox).copy()
        for bonfire in self.game.bonfires:
            if bonfire.pos in self.nearby_bonfires:
                self.nearby_bonfire_objects.append(bonfire)   

        # TODO collect souls if dropped and walk over them and then remove that drop and re-add souls to player-souls

        # Update melee attack duration
        if self.melee_hitbox is not None:
            self.update_melee_hitbox()
            self.melee_attack_duration -= 1
            if self.melee_attack_duration <= 0:
                # Reset melee hitbox after 10 frames
                self.melee_hitbox = None
                self.melee_attack_duration = 0
                self.is_melee_attacking = False 

        # Handle stamina and mana recovery
        for attack in self.attack_cooldowns:
            if self.attack_cooldowns[attack]['current'] > 0:
                self.attack_cooldowns[attack]['current'] -= 1

        if self.stamina < self.max_stamina and self.stamina_recovery_start:
            time_since_last_melee = pygame.time.get_ticks() - self.stamina_recovery_start
            if time_since_last_melee >= self.stamina_regen_cooldown:
                self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate)

        if self.mana < self.max_mana and self.mana_recovery_start:
            time_since_last_spell = pygame.time.get_ticks() - self.mana_recovery_start
            if time_since_last_spell >= self.mana_regen_cooldown:
                self.mana = min(self.max_mana, self.mana + self.mana_regen_rate)

        # Handle Death
        if self.health <= 0:
            self.die()

    def die(self):
        self.game.drops.clear()
        self.game.drop_particle_spawners.clear()
        if self.souls > 0:
            self.game.drops.append(Souls(self.game, 'soul', self.pos.copy(), self.souls))
            self.souls = 0
        self.pos = self.spawn_point.copy()
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.mana = self.max_mana
        self.knockback_velocity = [0, 0]
        self.is_facing = 'down'
        self.set_action('idle_down')

    def apply_knockback(self, knockback_vector, knockback_strength):
        distance = max(1, (knockback_vector[0] ** 2 + knockback_vector[1] ** 2) ** 0.5)
        normalized_vector = [knockback_vector[0] / distance, knockback_vector[1] / distance]

        self.knockback_velocity = [normalized_vector[0] * knockback_strength, normalized_vector[1] * knockback_strength]
        self.knockback_remaining = self.knockback_duration
        self.knockback_direction = 'horizontal' if abs(self.knockback_velocity[0]) > abs(self.knockback_velocity[1]) else 'vertical'

    def apply_knockback_movement(self):
        dx, dy = self.knockback_velocity

        # Separate the knockback into horizontal and vertical components
        # Try horizontal movement first, if blocked, move vertically or vice versa

        # Try moving horizontally
        if dx != 0:
            self.pos[0] += dx
            if self.handle_collisions('right' if dx > 0 else 'left'):
                # If horizontal movement is blocked, set horizontal velocity to 0
                dx = 0
        
        # Try moving vertically
        if dy != 0:
            self.pos[1] += dy
            if self.handle_collisions('down' if dy > 0 else 'up'):
                # If vertical movement is blocked, set vertical velocity to 0
                dy = 0

        # If both directions are blocked, stop knockback
        if dx == 0 and dy == 0:
            self.knockback_remaining = 0

        self.knockback_remaining -= 1

    def update_melee_hitbox(self):
        """Update the melee hitbox position based on the player's current position and facing direction."""
        if self.is_facing == 'up':
            self.melee_hitbox = pygame.Rect(self.pos[0] + 4, self.pos[1] - 14, 8, 18)
        elif self.is_facing == 'down':
            self.melee_hitbox = pygame.Rect(self.pos[0] + 4, self.pos[1] + 14, 8, 18)
        elif self.is_facing == 'left':
            self.melee_hitbox = pygame.Rect(self.pos[0] - 14, self.pos[1] + 4, 18, 8)
        elif self.is_facing == 'right':
            self.melee_hitbox = pygame.Rect(self.pos[0] + 12, self.pos[1] + 4, 18, 8)


    def melee(self):
        if self.attack_cooldowns['melee']['current'] == 0 and self.stamina >= 15:
            super().melee()

            self.stamina -= 15
            self.stamina_recovery_start = pygame.time.get_ticks()

            # Set the melee attack duration to 10 frames
            self.melee_attack_duration = 10
            self.is_melee_attacking = True

            for enemy in self.game.enemies:
                if self.melee_hitbox and self.melee_hitbox.colliderect(enemy.damage_rect()):
                    enemy.health -= 10
                    knockback_vector = [enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1]]
                    enemy.apply_knockback(knockback_vector, knockback_strength=3)

            self.attack_cooldowns['melee']['current'] = self.attack_cooldowns['melee']['max']

    def cast_spell(self):
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
                fireball = FireballSpell(self.game, (self.pos[0] + 2, self.pos[1] + 2), self.spell_velocity, self.vertical_spell, self.vertical_spell_flip)
                self.game.projectiles.append(fireball)

            self.mana -= self.spell_details[self.equipped_spell]['mana_cost']
            self.mana_recovery_start = pygame.time.get_ticks()

        else:
            print("Not enough mana to cast the spell.")

    def render(self, surf, offset=(0, 0)):

        # Render damage hitbox
        # hitbox_color = (255, 0, 0)
        # pygame.draw.rect(
        #     surf, 
        #     hitbox_color, 
        #     (self.pos[0] - offset[0] + self.damage_offset_x, self.pos[1] - offset[1] + self.damage_offset_y, self.damage_hitbox[0], self.damage_hitbox[1]), 
        #     1
        # )

        # #Render physics hitbox
        # physics_hitbox_color = (0, 0, 255)
        # pygame.draw.rect(
        #     surf, 
        #     physics_hitbox_color, 
        #     (self.pos[0] - offset[0] + self.physics_offset_x, self.pos[1] - offset[1] + self.physics_offset_y, self.physics_hitbox[0], self.physics_hitbox[1]), 
        #     1
        # )


        # Only render the weapon if melee_hitbox is not None
        if self.melee_hitbox is not None:
            # Select weapon image based on facing direction
            if self.is_facing in ['up', 'down']:
                weapon_image = self.game.assets[self.equipped_melee + '_vertical']
                flip_horizontally = False
                flip_vertically = self.is_facing == 'down'  # Flip vertically if facing down
            else:
                weapon_image = self.game.assets[self.equipped_melee + '_horizontal']
                flip_horizontally = self.is_facing == 'left'  # Flip horizontally if facing left
                flip_vertically = False

            # Flip the weapon image based on direction
            weapon_image = pygame.transform.flip(weapon_image, flip_horizontally, flip_vertically)
            
            # Align the weapon position with the melee hitbox
            weapon_pos = (self.melee_hitbox.x - offset[0], self.melee_hitbox.y - offset[1])

            if self.is_facing in ['up']:
                weapon_pos = (self.melee_hitbox.x - offset[0], self.melee_hitbox.y - offset[1])
            elif self.is_facing in ['down']:
                weapon_pos = (self.melee_hitbox.x - offset[0], self.melee_hitbox.y - offset[1])

            # Blit (draw) the weapon image on the surface
            surf.blit(weapon_image, weapon_pos)

        # Render the player sprite
        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (self.pos[0] - offset[0] + self.anim_offset[0],
            self.pos[1] - offset[1] + self.anim_offset[1])
        )
        
        # Optionally draw the melee hitbox for debugging
        # if self.melee_hitbox is not None:
        #     melee_hitbox_color = (0, 255, 0)
        #     pygame.draw.rect(surf, melee_hitbox_color, 
        #                     pygame.Rect(self.melee_hitbox.x - offset[0], 
        #                                 self.melee_hitbox.y - offset[1], 
        #                                 self.melee_hitbox.width, 
        #                                 self.melee_hitbox.height), 1)


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, damage_hitbox, physics_hitbox):
        super().__init__(game, 'skeleton', pos, damage_hitbox, physics_hitbox)
        self.health = 25
        self.max_health = 25
        self.speed = 0.5
        self.knockback_velocity = [0, 0]
        self.knockback_duration = 10
        self.knockback_remaining = 0
        self.knockback_direction = None
        self.souls = 100

    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        if self.knockback_remaining > 0:
            self.apply_knockback_movement()
        else:
            direction_x = self.game.player.pos[0] - self.pos[0]
            direction_y = self.game.player.pos[1] - self.pos[1]
            distance = max(1, (direction_x ** 2 + direction_y ** 2) ** 0.5)

            move_x = self.speed * (direction_x / distance)
            move_y = self.speed * (direction_y / distance)

            movement_x = [False, False]
            movement_y = [False, False]

            if abs(move_y) > 0.25:
                if move_y < 0:
                    movement_y[0] = abs(move_y)
                else:
                    movement_y[1] = abs(move_y)

            if abs(move_x) > 0.25:
                if move_x < 0:
                    movement_x[0] = abs(move_x)
                else:
                    movement_x[1] = abs(move_x)

            super().update(movement_x, movement_y)

        if self.physics_rect().colliderect(self.game.player.physics_rect()):
            self.apply_damage_to_player()
            self.apply_knockback_to_player()

        for enemy in self.game.enemies:
            if enemy != self and self.physics_rect().colliderect(enemy.physics_rect()):
                self.prevent_overlap(enemy)

                # Only apply knockback to the other enemy if this enemy is currently being knocked back
                if self.knockback_remaining > 0:
                    self.apply_knockback_to_other_enemy(enemy)

        if self.health <= 0:
            self.die()

    def apply_knockback(self, knockback_vector, knockback_strength):
        distance = max(1, (knockback_vector[0] ** 2 + knockback_vector[1] ** 2) ** 0.5)
        normalized_vector = [knockback_vector[0] / distance, knockback_vector[1] / distance]

        self.knockback_velocity = [normalized_vector[0] * knockback_strength, normalized_vector[1] * knockback_strength]
        self.knockback_remaining = self.knockback_duration
        self.knockback_direction = 'horizontal' if abs(self.knockback_velocity[0]) > abs(self.knockback_velocity[1]) else 'vertical'

    def apply_knockback_movement(self):
        dx, dy = self.knockback_velocity

        # Separate the knockback into horizontal and vertical components
        # Try horizontal movement first, if blocked, move vertically or vice versa

        # Try moving horizontally
        if dx != 0:
            self.pos[0] += dx
            if self.handle_collisions('right' if dx > 0 else 'left'):
                # If horizontal movement is blocked, set horizontal velocity to 0
                dx = 0
        
        # Try moving vertically
        if dy != 0:
            self.pos[1] += dy
            if self.handle_collisions('down' if dy > 0 else 'up'):
                # If vertical movement is blocked, set vertical velocity to 0
                dy = 0

        # If both directions are blocked, stop knockback
        if dx == 0 and dy == 0:
            self.knockback_remaining = 0

        self.knockback_remaining -= 1

    def prevent_overlap(self, other_enemy):
        """Prevent enemies from overlapping."""
        overlap_rect = self.physics_rect().clip(other_enemy.physics_rect())

        # Prevent overlap by adjusting positions without applying knockback
        if overlap_rect.width > overlap_rect.height:
            if self.pos[1] < other_enemy.pos[1]:
                self.pos[1] -= overlap_rect.height
            else:
                self.pos[1] += overlap_rect.height
        else:
            if self.pos[0] < other_enemy.pos[0]:
                self.pos[0] -= overlap_rect.width
            else:
                self.pos[0] += overlap_rect.width

    def apply_knockback_to_other_enemy(self, other_enemy):
        """Apply knockback to the other enemy during a collision, only if this enemy is being knocked back."""
        knockback_vector = [other_enemy.pos[0] - self.pos[0], other_enemy.pos[1] - self.pos[1]]
        knockback_strength = 2  # Adjust knockback strength for enemy-to-enemy knockback
        other_enemy.apply_knockback(knockback_vector, knockback_strength)

    def apply_damage_to_player(self):
        damage = 5
        self.game.player.health -= damage

    def apply_knockback_to_player(self):
        knockback_strength = 3
        dx = self.game.player.pos[0] - self.pos[0]
        dy = self.game.player.pos[1] - self.pos[1]
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)

        knockback_vector = [knockback_strength * (dx / distance), knockback_strength * (dy / distance)]
        self.game.player.apply_knockback(knockback_vector, knockback_strength)

    def die(self):
        super().die()

    def render(self, surf, offset=(0, 0)):

        # Render damage hitbox
        # hitbox_color = (255, 0, 0)
        # pygame.draw.rect(
        #     surf,
        #     hitbox_color,
        #     (self.pos[0] - offset[0] + self.damage_offset_x, self.pos[1] - offset[1] + self.damage_offset_y, self.damage_hitbox[0], self.damage_hitbox[1]),
        #     1
        # )

        # # Render physics hitbox
        # physics_hitbox_color = (0, 0, 255)
        # pygame.draw.rect(
        #     surf, 
        #     physics_hitbox_color, 
        #     (self.pos[0] - offset[0] + self.physics_offset_x, self.pos[1] - offset[1] + self.physics_offset_y, self.physics_hitbox[0], self.physics_hitbox[1]), 
        #     1
        # )

        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (self.pos[0] - offset[0] + self.anim_offset[0],
             self.pos[1] - offset[1] + self.anim_offset[1])
        )
import pygame
import random
import asyncio
import sys
import json
import numpy as np
from collections import deque

from scripts.drop import Drop, Souls
from scripts.tilemap import Tilemap
from scripts.weapon import Weapon
from scripts.spell import Spell
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


        # Normalize diagonal movement

        # Up/left
        if movement_x[0] and movement_y[0]:
            movement_x[0], movement_y[0] = 0.7, 0.7
        # Up/Right
        if movement_x[1] and movement_y[0]:
            movement_x[1], movement_y[0] = 0.7, 0.7
        # Down/Left
        if movement_x[0] and movement_y[1]:
            movement_x[0], movement_y[1] = 0.7, 0.7
        # Down/Right
        if movement_x[1] and movement_y[1]:
            movement_x[1], movement_y[1] = 0.7, 0.7

        # Because we detect movement changes on key down and key-up, we must set the movement back to 1 if the player is moving diagonally and a key is let go
        if movement_x[0] == 0.7 and (not movement_y[0] and not movement_y[1]):
            movement_x[0] = 1
        if movement_x[1] == 0.7  and (not movement_y[0] and not movement_y[1]):
            movement_x[1] = 1
        if movement_y[0] == 0.7  and (not movement_x[0] and not movement_x[1]):
            movement_y[0] = 1
        if movement_y[1] == 0.7  and (not movement_x[0] and not movement_x[1]):
            movement_y[1] = 1
        
        # Process vertical movement first
        if movement_y[0] > 0:  # Moving up
            self.pos[1] -= movement_y[0]
            self.handle_collisions('up')
            self.is_facing = 'up'
            self.flip = False
            if movement_x[0] == 0 and movement_x[1] == 0:
                self.set_action('walking_up')
        if movement_y[1] > 0:  # Moving down
            self.pos[1] += movement_y[1]
            self.handle_collisions('down')
            self.is_facing = 'down'
            self.flip = False
            if movement_x[0] == 0 and movement_x[1] == 0:
                self.set_action('walking_down')
                
        # Process horizontal movement second
        if movement_x[0] > 0:  # Moving left
            self.pos[0] -= movement_x[0]
            self.handle_collisions('left')
            self.is_facing = 'left'
            self.flip = True
            self.set_action('walking_horizontal')
        if movement_x[1] > 0:  # Moving right
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
                    self.patrol_direction = None
                    self.patrol_counter = 1
                elif direction == 'right':
                    self.collisions['right'] = True
                    self.pos[0] = rect.left - self.physics_hitbox[0] - 1
                    self.patrol_direction = None
                    self.patrol_counter = 1
                elif direction == 'up':
                    self.collisions['up'] = True
                    self.pos[1] = rect.bottom - self.physics_offset_y
                    self.patrol_direction = None
                    self.patrol_counter = 1
                elif direction == 'down':
                    self.collisions['down'] = True
                    self.pos[1] = rect.top - self.physics_hitbox[1] - self.physics_offset_y
                    self.patrol_direction = None
                    self.patrol_counter = 1

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
        self.level = 1
        self.melee_hitbox = None
        self.image = self.game.assets['player']
        self.is_facing = 'down'
        self.vertical_spell = False
        self.vertical_spell_flip = False
        self.melee_attack_duration = 0 
        self.is_melee_attacking = False
        self.nearby_bonfires = []
        self.nearby_bonfire_objects = []
        self.weapon_inventory = [Weapon(self.game, 'basic_sword', 10, 30, 10),]
        self.equipped_weapon = self.weapon_inventory[0]
        self.spell_inventory = [Spell(self.game, 'fireball', 20, 10, 2, 0),]
        self.equipped_spell = self.spell_inventory[0]

        self.stamina_recovery_start = None
        self.stamina_regen_cooldown = 2000
        self.stamina_regen_rate = 1

        self.mana_recovery_start = None
        self.mana_regen_cooldown = 2000
        self.mana_regen_rate = 0.02

        self.attack_cooldown = 0

        self.knockback_velocity = [0, 0]
        self.knockback_duration = 10
        self.knockback_remaining = 0
        self.knockback_direction = None

    def open_chest(self):
        chest = self.nearby_chest_objects[0]
        
        # TODO Item stuff
        chest.drop_items()


    def rest_at_bonfire(self):
        if len(self.nearby_bonfires) > 0:
            self.spawn_point = [self.nearby_bonfire_objects[0].pos[0] + 8, self.nearby_bonfire_objects[0].pos[1] + 32]
            self.pos = self.spawn_point.copy()
            self.health = self.max_health
            self.stamina = self.max_stamina
            self.mana = self.max_mana
            self.is_facing = 'down'
            self.game.movement_x[0] = False
            self.game.movement_x[1] = False
            self.game.movement_y[0] = False
            self.game.movement_y[1] = False
            self.set_action('idle_down')
            
            # Save open chests
            open_chests = {self.game.tilemap.current_level : []}
            for chest in self.game.chests:
                if chest.is_opened:
                    open_chests[self.game.tilemap.current_level].append((chest.pos[0], chest.pos[1]))

            # Equipped weapon to dict
            self.equipped_weapon_data = self.equipped_weapon.to_dict()

            # equipped spell to dict
            self.equipped_spell_data = self.equipped_spell.to_dict()

            # non-equipped weapons to dict
            weapons = []
            for weapon in self.weapon_inventory:
                if weapon is not self.equipped_weapon:
                    weapons.append(weapon.to_dict())
            # non-equipped spells to dict 
            spells = []
            for spell in self.spell_inventory:
                if spell is not self.equipped_spell:
                    spells.append(spell.to_dict())

            # Information to save into JSON file
            data = {
            'max_health' : self.max_health,
            'max_stamina' : self.max_stamina,
            'max_mana' : self.max_mana,
            'souls' : self.souls,
            'equipped_weapon' : self.equipped_weapon_data,
            'weapons_inventory' : weapons,
            'equipped_spell' : self.equipped_spell_data,
            'spells_inventory' : spells,
            'spawn_point' : self.spawn_point,
            'level' : self.level,
            'open_chests' : open_chests,
            }

            with open('save_files/save.json', 'w') as save_file:
                json.dump(data, save_file)
        
        
            # trigger upgrade screen gameloop
            self.game.reset_enemies()
            self.game.fade_out()
            self.game.upgrade_screen()
    
    def update(self, movement_x=(0, 0), movement_y=(0, 0)):

        # Reset Nearby Bonfires
        self.nearby_bonfires = []
        self.nearby_bonfire_objects = []

        # Rest Nearby Chests
        self.nearby_chests = []
        self.nearby_chest_objects = []

        if self.knockback_remaining > 0:
            self.apply_knockback_movement()
        elif not self.is_melee_attacking:
            super().update(movement_x, movement_y)

        # Check For Nearby Bonfires
        self.nearby_bonfires = self.game.tilemap.bonfires_around((self.pos[0] + self.physics_offset_x, self.pos[1] + self.physics_offset_y), self.physics_hitbox).copy()
        for bonfire in self.game.bonfires:
            if bonfire.pos in self.nearby_bonfires:
                self.nearby_bonfire_objects.append(bonfire)   

        # check for nearby chests
        self.nearby_chests = self.game.tilemap.chests_around((self.pos[0] + self.physics_offset_x, self.pos[1] + self.physics_offset_y), self.physics_hitbox).copy()
        for chest in self.game.chests:
            if chest.pos in self.nearby_chests:
                self.nearby_chest_objects.append(chest)        

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
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.stamina < self.max_stamina and self.stamina_recovery_start:
            time_since_last_melee = pygame.time.get_ticks() - self.stamina_recovery_start
            if time_since_last_melee >= self.stamina_regen_cooldown:
                self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate)

        if self.mana < self.max_mana and self.mana_recovery_start:
            time_since_last_spell = pygame.time.get_ticks() - self.mana_recovery_start
            if time_since_last_spell >= self.mana_regen_cooldown:
                self.mana = min(self.max_mana, self.mana + self.mana_regen_rate)

        self.game.tilemap.insert_entity_into_physics_tilemap(self.pos, 'player')

        # Handle Death
        if self.health <= 0:
            self.die()

    def die(self):
        self.game.drops.clear()
        self.game.drop_particle_spawners.clear()
        if self.souls > 0:
            self.game.drops.append(Souls(self.game, self.pos.copy(), 'souls', self.game.assets['dropped_souls'], self.souls))
            self.souls = 0
        self.pos = self.spawn_point.copy()
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.mana = self.max_mana
        self.knockback_velocity = [0, 0]
        self.is_facing = 'down'
        self.set_action('idle_down')
        self.game.reset_enemies()

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
        if self.attack_cooldown == 0 and self.stamina >= self.equipped_weapon.stamina_cost:
            super().melee()

            self.stamina -= self.equipped_weapon.stamina_cost
            self.stamina_recovery_start = pygame.time.get_ticks()

            # Set the melee attack duration to 10 frames
            self.melee_attack_duration = 10
            self.is_melee_attacking = True

            for enemy in self.game.enemies:
                if self.melee_hitbox and self.melee_hitbox.colliderect(enemy.damage_rect()):
                    enemy.health -= self.equipped_weapon.damage
                    knockback_vector = [enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1]]
                    enemy.apply_knockback(knockback_vector, knockback_strength=3)

            self.attack_cooldown = self.equipped_weapon.cooldown

    def cast_spell(self):
        if self.mana >= self.equipped_spell.mana_cost:
            if self.is_facing == 'up':
                self.spell_velocity = [0, -self.equipped_spell.velocity]
                self.vertical_spell = True
                self.vertical_spell_flip = True
            if self.is_facing == 'down':
                self.spell_velocity = [0, self.equipped_spell.velocity]
                self.vertical_spell = True
                self.vertical_spell_flip = False
            if self.is_facing == 'left':
                self.spell_velocity = [-self.equipped_spell.velocity, 0]
                self.vertical_spell = False
                self.vertical_spell_flip = False
            if self.is_facing == 'right':
                self.spell_velocity = [self.equipped_spell.velocity, 0]
                self.vertical_spell = False
                self.vertical_spell_flip = False
            if self.equipped_spell.spell_type == 'fireball':
                fireball = FireballSpell(self.game, (self.pos[0] + 2, self.pos[1] + 8), self.spell_velocity, self.vertical_spell, self.vertical_spell_flip, self.equipped_spell.damage)
                self.game.projectiles.append(fireball)
            if self.equipped_spell.spell_type == 'lightning':
                pass

            self.mana -= self.equipped_spell.mana_cost
            self.mana_recovery_start = pygame.time.get_ticks()

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
                weapon_image = self.game.assets[self.equipped_weapon.weapon_type + '_vertical']
                flip_horizontally = False
                flip_vertically = self.is_facing == 'down'  # Flip vertically if facing down
            else:
                weapon_image = self.game.assets[self.equipped_weapon.weapon_type + '_horizontal']
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
        self.spawn_point = self.pos.copy()
        # patrol stuff
        self.patrol_counter = 0
        self.pause_counter = 0
        self.move_x = 0
        self.move_y = 0
        self.patrol_area_x = [self.pos[0] - 50, self.pos[0] + 50]
        self.patrol_area_y = [self.pos[1] - 50, self.pos[1] + 50]
        self.patrol_area_center = self.pos.copy()
        self.patrol_direction = None
        # pursuit stuff
        self.pursuit = False
        self.path = None
        self.current_tile = None
        self.traveling = False
        self.pursuit_direction = None
        self.start = None
        self.next = None

    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        if self.knockback_remaining > 0:
            self.apply_knockback_movement()
            self.patrol_counter = -1
        else:
            direction_x = self.game.player.pos[0] - self.pos[0]
            direction_y = self.game.player.pos[1] - self.pos[1]
            if self.pursuit:
                self.move_x = 0
                self.move_y = 0
            distance = max(1, (direction_x  ** 2 + direction_y ** 2) ** 0.5)
            movement_x = [False, False]
            movement_y = [False, False]

            # Start pursuit
            
            if distance < 75 or (distance < 100 and self.pursuit):
                self.pursuit = True
                if self.path is None or self.path[len(self.path) - 1] != ((self.game.player.pos[1] + 4) // 16, (self.game.player.pos[0] + 7) // 16):
                    tilemap = self.game.tilemap.insert_entity_into_physics_tilemap(self.pos, 'enemy')
                    self.path = self.construct_path(tilemap)
                    self.pursuit_direction = None
                else:
                    if len(self.path) >= 2 and not self.traveling:
                        self.start = self.path[0]
                        self.next = self.path[1]
                        if self.start[1] < self.next[1]:
                            # Right
                            self.move_x = 1
                            self.pursuit_direction = 'right'
                        elif self.start[1] > self.next[1]:
                            # Left
                            self.move_x = -1
                            self.pursuit_direction = 'left'
                        elif self.start[0] < self.next[0]:
                            # Up
                            self.move_y = 1
                            self.pursuit_direction = 'down'
                        elif self.start[0] > self.next[0]:
                            # Down 
                            self.move_y = -1
                            self.pursuit_direction = 'up'
                        if len(self.path) == 2:
                            self.current_tile = self.path[0]
                        self.traveling = True
                    if self.traveling:
                        # TODO better handling of this lol
                        if self.pursuit_direction == 'right' and (self.pos[0] + 9) // 16 <= self.next[1]:
                            self.move_x = 1 * self.speed
                        elif self.pursuit_direction == 'left' and (self.pos[0] - 7) // 16 >= self.next[1]:
                            self.move_x = -1 * self.speed
                        elif self.pursuit_direction == 'up' and (self.pos[1] - 4) // 16 >= self.next[0]:
                            self.move_y = -1 * self.speed
                        elif self.pursuit_direction == 'down' and (self.pos[1] + 12) // 16 <= self.next[0]:
                            self.move_y = 1 * self.speed
                        else: 
                            self.pursuit_direction = None
                            self.traveling = False
                            del self.path[0]     
                        if len(self.path) == 2:
                            self.traveling = False                      
                    else:
                        self.move_x = self.speed * (direction_x / distance)
                        self.move_y = self.speed * (direction_y / distance)
                        


            # If was pursuiting, update patrol area once player escapes
            elif self.pursuit:
                self.patrol_area_x = [self.pos[0] - 50, self.pos[0] + 50]
                self.patrol_area_y = [self.pos[1] - 50, self.pos[1] + 50]
                self.pursuit = False
                self.pause_counter = random.randint(10, 30)
                self.patrol_counter = 0.5
            elif self.pos[0] < self.patrol_area_x[0] or self.pos[0] > self.patrol_area_x[1] or self.pos[1] < self.patrol_area_y[0] or self.pos[1] > self.patrol_area_y[1]:
                self.patrol_area_x = [self.pos[0] - 50, self.pos[0] + 50]
                self.patrol_area_y = [self.pos[1] - 50, self.pos[1] + 50]
                direction_x = self.patrol_area_center[0] - self.pos[0]
                direction_y = self.patrol_area_center[1] - self.pos[1]
                distance = max(1, (direction_x ** 2 + direction_y ** 2) ** 0.5)
                self.move_x = self.speed * (direction_x / distance)
                self.move_y = self.speed * (direction_y / distance)
                # If pursuit and no longer in range to chase player
                if abs(self.pos[0] - self.patrol_area_center[0] < 20) and abs(self.pos[1] - self.patrol_area_center[1] < 20):
                    self.pursuit = False
                    self.pause_counter = random.randint(10, 30)
                    self.patrol_counter = 0.5

            # Patrol
            elif self.patrol_counter <= 0:
                self.patrol_direction = ['up', 'down', 'left', 'right'][(random.randint(0, 3))]
                self.patrol_counter = random.randint(100, 200)
                if self.patrol_direction == 'up':
                    self.move_x = 0
                    self.move_y = -0.3
                elif self.patrol_direction  == 'down':
                    self.move_x = 0
                    self.move_y = 0.3
                elif self.patrol_direction == 'left':
                    self.move_x = -0.3
                    self.move_y = 0
                else:
                    self.move_x = 0.3
                    self.move_y = 0

            # End patrol and start pause
            elif self.patrol_counter == 1:
                self.pause_counter = random.randint(100, 200)
                self.move_x = 0
                self.move_y = 0
                self.patrol_counter = 0.5
            # Iterate pause
            elif self.pause_counter >= 0:
                self.pause_counter -= 1
            # End pause start new patrol
            elif self.pause_counter < 0 and self.patrol_counter == 0.5:
                self.pause_counter = 0
                self.patrol_counter = 0
            # If exits patrol area during patrol
            else:
                if self.pos[0] < self.patrol_area_x[0] and self.patrol_direction == 'left':
                    self.patrol_direction == 'right'
                    self.patrol_counter *= 2
                    self.move_x *= -1
                elif self.pos[0] > self.patrol_area_x[1] and self.patrol_direction == 'right':
                    self.patrol_direction == 'left'
                    self.patrol_counter *= 2
                    self.move_x *= -1
                elif self.pos[1] < self.patrol_area_y[0] and self.patrol_direction == 'up':
                    self.patrol_direction == 'down'
                    self.patrol_counter *= 2
                    self.move_y *= -1
                elif self.pos[1] > self.patrol_area_y[1] and self.patrol_direction == 'down':
                    self.patrol_direction == 'up'
                    self.patrol_counter *= 2
                    self.move_y *= -1
                else:
                    self.patrol_counter -= 1

            # Handle movement
            if abs(self.move_y) > 0.25:
                if self.move_y < 0:
                    # up
                    movement_y[0] = abs(self.move_y)
                else:
                    # down
                    movement_y[1] = abs(self.move_y)

            if abs(self.move_x) > 0.25:
                if self.move_x < 0:
                    # left
                    movement_x[0] = abs(self.move_x)
                else:
                    # right
                    movement_x[1] = abs(self.move_x)

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

    # BFS algorithm for finding path from 3 to 2 in physcis_tilemap
    def find_start_and_target(self, physics_tilemap):
        start = None
        target = None
        for i in range(len(physics_tilemap)):
            for j in range(len(physics_tilemap[i])):
                if physics_tilemap[i][j] == 3:
                    start = (i, j)
                if physics_tilemap[i][j] == 2:
                    target = (i, j)
        return start, target
    
    # BFS algorithm for finding path from 3 to 2 in physcis_tilemap
    def bfs(self, physics_tilemap, start, target):
        if start is None or target is None:
            return None  # Return if either start or target is not found

        rows, cols = len(physics_tilemap), len(physics_tilemap[0])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
        queue = deque([start])
        visited = set([start])
        parent = {start: None}

        while queue:
            current = queue.popleft()

            # Stop if the current node is the target
            if current == target:
                path = []
                step = target
                while step is not None:
                    path.append(step)
                    step = parent[step]
                path.reverse()
                return path  # Return the path from start to target

            # Explore neighbors
            for direction in directions:
                new_row, new_col = current[0] + direction[0], current[1] + direction[1]
                new_position = (new_row, new_col)

                # Check if the new position is within bounds, has not been visited, and is not an impassable cell (1)
                if (0 <= new_row < rows and 0 <= new_col < cols and
                        new_position not in visited and physics_tilemap[new_row][new_col] != 1):
                    
                    queue.append(new_position)
                    visited.add(new_position)
                    parent[new_position] = current

        # If we exhaust the queue and do not find the target, return None
        return None
        

    def construct_path(self, physics_tilemap):
        start, target = self.find_start_and_target(physics_tilemap)
        if not start or not target:
            return None
        return self.bfs(physics_tilemap, start, target)

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
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
        pass
    
    def melee(self):
        self.melee_attack = True
        if self.is_facing == 'up':
            self.melee_hitbox = pygame.Rect(self.pos[0]+4, self.pos[1] - 14, 8, 18)
        elif self.is_facing == 'down':
            self.melee_hitbox = pygame.Rect(self.pos[0]+4, self.pos[1] + 4, 8, 18)
        elif self.is_facing == 'left':
            self.melee_hitbox = pygame.Rect(self.pos[0]-14, self.pos[1], 18, 8)
        elif self.is_facing == 'right':
            self.melee_hitbox = pygame.Rect(self.pos[0]+12, self.pos[1], 18, 8)
        if self.melee_attack == True:
            self.can_attack = True
            
    def handle_collisions(self, direction):
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos, self.size):
            if entity_rect.colliderect(rect):
                if direction == 'left':
                    self.collisions['left'] = True
                    self.pos[0] = rect.right
                elif direction == 'right':
                    self.collisions['right'] = True
                    self.pos[0] = rect.left - self.size[0]
                elif direction == 'up':
                    self.collisions['up'] = True
                    self.pos[1] = rect.bottom
                elif direction == 'down':
                    self.collisions['down'] = True
                    self.pos[1] = rect.top - self.size[1]

    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0], 
                   self.pos[1] - offset[1] + self.anim_offset[1]))


# Class for the player character
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
        self.spell_velocity = [0, 0]
        self.is_facing = 'down'
        self.vertical_spell = False
        self.vertical_spell_flip = False

        self.attack_cooldowns = {
            'melee': {'current': 0, 'max': 60},
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

    def update(self, movement_x=(0, 0), movement_y=(0, 0)):
        if self.knockback_remaining > 0:
            self.apply_knockback_movement()
        else:
            super().update(movement_x, movement_y)

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

    def melee(self):
        if self.attack_cooldowns['melee']['current'] == 0 and self.stamina >= 15:
            super().melee()

            self.stamina -= 15
            self.stamina_recovery_start = pygame.time.get_ticks()

            for enemy in self.game.enemies:
                if self.melee_hitbox and self.melee_hitbox.colliderect(enemy.rect()):
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
        hitbox_color = (255, 0, 0)
        pygame.draw.rect(
            surf, 
            hitbox_color, 
            (self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1]), 
            1
        )

        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0],
                   self.pos[1] - offset[1] + self.anim_offset[1] - 6))
        
        if self.melee_hitbox is not None:
            melee_hitbox_color = (0, 255, 0)
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
        self.speed = 0.5
        self.knockback_velocity = [0, 0]
        self.knockback_duration = 10
        self.knockback_remaining = 0
        self.knockback_direction = None

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

        if self.rect().colliderect(self.game.player.rect()):
            self.apply_damage_to_player()
            self.apply_knockback_to_player()

        for enemy in self.game.enemies:
            if enemy != self and self.rect().colliderect(enemy.rect()):
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
        overlap_rect = self.rect().clip(other_enemy.rect())

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

    def handle_collisions(self, direction):
        entity_rect = self.rect()
        for rect in self.game.tilemap.physics_rects_around(self.pos, self.size):
            if entity_rect.colliderect(rect):
                if direction == 'left':
                    self.collisions['left'] = True
                    self.pos[0] = rect.right
                    return True
                elif direction == 'right':
                    self.collisions['right'] = True
                    self.pos[0] = rect.left - self.size[0]
                    return True
                elif direction == 'up':
                    self.collisions['up'] = True
                    self.pos[1] = rect.bottom
                    return True
                elif direction == 'down':
                    self.collisions['down'] = True
                    self.pos[1] = rect.top - self.size[1]
                    return True
        return False

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
        self.game.enemies.remove(self)

    def render(self, surf, offset=(0, 0)):
        hitbox_color = (255, 0, 0)
        pygame.draw.rect(
            surf,
            hitbox_color,
            (self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1]),
            1
        )

        surf.blit(
            pygame.transform.flip(self.animation.img(), self.flip, False),
            (self.pos[0] - offset[0] + self.anim_offset[0],
             self.pos[1] - offset[1] + self.anim_offset[1] - 6)
        )
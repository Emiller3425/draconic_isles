import pygame
import math

class Projectile:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0, size=None):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['' + p_type].copy()
        self.animation_frame = frame
        
        img = self.animation.img()
        self.size = size if size else (img.get_width(), img.get_height())

    def update(self):
        kill = False
        if self.animation.done:
            kill = True
        if self.check_collision():
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill

    def check_collision(self):
        for enemy in self.game.enemies:
            if enemy.damage_rect().colliderect(self.rect()):
                knockback_vector = [enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1]]
                enemy.apply_knockback(knockback_vector, knockback_strength=5)
                enemy.take_damage(10)  # Deal 10 damage to the enemy
                return True
        return False
            
    def rect(self):
        return pygame.Rect(
            self.pos[0] - self.size[0] // 2,
            self.pos[1] - self.size[1] // 2,
            self.size[0],
            self.size[1]
        )

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

class FireballSpell(Projectile):
    def __init__(self, game, pos, velocity, vertical, vertical_flip):
        if vertical:
            super().__init__(game, 'fireballspell_vertical', (game.player.pos[0] + 8, pos[1]), velocity, size=(20, 20))
        else:
            super().__init__(game, 'fireballspell_horizontal', pos, velocity, size=(20, 20))
        self.knockback_strength = 5  # Specify the fireball knockback strength
        self.max_distance = 10 * 16  # Maximum distance (15 tiles, each 16 pixels)
        self.distance_traveled = 0
        self.exploding = False  # To track if the fireball is exploding
        self.explosion_duration = 10  # Time for the explosion animation
        self.explosion_hitbox_size = (25, 25)  # Explosion hitbox size
        self.flip = self.game.player.flip
        self.vertical_flip = vertical_flip
        self.damaged_entities = []  # List to track entities that have already taken damage
        self.damage = 10  # Damage dealt by the fireball
        self.explosion_damage = 10  # Damage dealt by the explosion

    def update(self):
        if self.exploding:
            self.explosion_duration -= 1
            if self.explosion_duration <= 0:
                return True  # End the fireball after the explosion
            self.animation.update()
            self.check_explosion_collision()
            return False
        
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.distance_traveled += math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

        if self.distance_traveled >= self.max_distance:
            self.explode()
            return False

        if self.check_collision():
            self.explode()
            return False

        self.animation.update()
        return False

    def explode(self):
        self.exploding = True
        self.animation = self.game.assets['fireballspell_impact'].copy()
        self.size = self.explosion_hitbox_size

    def check_explosion_collision(self):
        for enemy in self.game.enemies:
            if enemy not in self.damaged_entities and enemy.damage_rect().colliderect(self.rect()):
                # Calculate knockback based on the center of the explosion and enemy
                explosion_center = [self.pos[0], self.pos[1]]
                enemy_center = [enemy.pos[0] + enemy.damage_hitbox[0] // 2, enemy.pos[1] + enemy.damage_hitbox[1] // 2]
                knockback_vector = [enemy_center[0] - explosion_center[0], enemy_center[1] - explosion_center[1]]

                enemy.apply_knockback(knockback_vector, knockback_strength=self.knockback_strength)
                enemy.health -= self.explosion_damage  # Explosion deals 5 damage to enemies
                self.damaged_entities.append(enemy)

        if self.game.player not in self.damaged_entities and self.game.player.damage_rect().colliderect(self.rect()):
            # Calculate knockback based on the center of the explosion and player
            explosion_center = [self.pos[0], self.pos[1]]
            player_center = [self.game.player.pos[0] + self.game.player.damage_hitbox[0] // 2, self.game.player.pos[1] + self.game.player.damage_hitbox[1] // 2]
            knockback_vector = [player_center[0] - explosion_center[0], player_center[1] - explosion_center[1]]

            self.game.player.apply_knockback(knockback_vector, knockback_strength=self.knockback_strength)
            self.game.player.health -= self.explosion_damage * 2  # Explosion deals 15 damage to the player
            self.damaged_entities.append(self.game.player)

    def check_collision(self):
        for enemy in self.game.enemies:
            if enemy.damage_rect().colliderect(self.rect()):
                if not self.exploding:
                    enemy.health -= self.explosion_damage  # Fireball deals 10 damage
                    # knockback_vector = [enemy.pos[0] - self.pos[0], enemy.pos[1] - self.pos[1]]
                    # enemy.apply_knockback(knockback_vector, knockback_strength=self.knockback_strength)  # Apply knockback
                return True
        return False

    def rect(self):
        if not self.exploding:
            return pygame.Rect(
                self.pos[0] - self.size[0] // 2,
                self.pos[1] - self.size[1] // 2 + 2,
                self.size[0],
                self.size[1] - 4
            )
        else:
            return pygame.Rect(
                self.pos[0] - self.size[0] // 2,
                self.pos[1] - self.size[1] // 2,
                self.size[0],
                self.size[1]
            )

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, self.vertical_flip), 
                  (self.pos[0] - offset[0] - img.get_width() // 2, 
                   self.pos[1] - offset[1] - img.get_height() // 2))

        hitbox = self.rect().move(-offset[0], -offset[1])
        # Green hitbox for debugging
        # pygame.draw.rect(surf, (0, 255, 0), hitbox, 1)

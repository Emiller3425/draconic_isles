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
            if enemy.rect().colliderect(self.rect()):
                enemy.apply_knockback(self.knockback)
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
        # Draw the projectile image
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))
        # Draw the hitbox rectangle
        # hitbox = self.rect().move(-offset[0], -offset[1])
        # pygame.draw.rect(surf, (0, 255, 0), hitbox, 1)

class FireballSpell(Projectile):
    def __init__(self, game, pos, velocity, vertical, vertical_flip):
        if vertical == True:
            super().__init__(game, 'fireballspell_vertical', pos, velocity, size=(16, 16))
        else:
            super().__init__(game, 'fireballspell_horizontal', pos, velocity, size=(16, 16))
        self.knockback = 20
        self.max_distance = 10 * 16  # Maximum distance (15 tiles, each 16 pixels)
        self.distance_traveled = 0
        self.exploding = False  # To track if the fireball is exploding
        self.explosion_duration = 10  # Time for the explosion animation
        self.explosion_hitbox_size = (16, 16)  # Explosion hitbox size
        self.flip = self.game.player.flip
        self.vertical_flip = vertical_flip
        self.damaged_entities = []  # List to track entities that have already taken damage


    def update(self):
        # If exploding, handle the explosion animation
        if self.exploding:
            self.explosion_duration -= 1
            if self.explosion_duration <= 0:
                return True  # End the fireball after the explosion
            self.animation.update()

            # Check if the player or enemies are within the explosion hitbox
            self.check_explosion_collision()

            return False
        
        # Calculate the next position and check if it exceeds the max distance
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        # Update distance traveled
        self.distance_traveled += math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2)

        if self.distance_traveled >= self.max_distance:
            self.explode()
            return False

        # Check if collision occurs
        if self.check_collision():
            self.explode()
            return False

        # Update the animation
        self.animation.update()
        return False

    def explode(self):
        self.exploding = True
        # Switch to the explosion animation
        self.animation = self.game.assets['fireballspell_impact'].copy()
        self.size = self.explosion_hitbox_size  # Set the size of the explosion hitbox
        # You can add explosion damage logic here if needed

    def check_explosion_collision(self):
        # Check if enemies are in the explosion radius
        for enemy in self.game.enemies:
            if enemy not in self.damaged_entities and enemy.rect().colliderect(self.rect()):
                enemy.health -= 15  # Explosion deals 15 damage to enemies
                self.damaged_entities.append(enemy)  # Mark this enemy as damaged
        
        # Check if the player is in the explosion radius
        if self.game.player not in self.damaged_entities and self.game.player.rect().colliderect(self.rect()):
            self.game.player.health -= 15  # Explosion deals 15 damage to the player
            self.damaged_entities.append(self.game.player)  # Mark the player as damaged

    def check_collision(self):
        for enemy in self.game.enemies:
            if enemy.rect().colliderect(self.rect()):
                # Only apply knockback and damage during flight, not during explosion
                if not self.exploding:
                    enemy.health -= 10 # Fireball deals 10 damage
                return True
        return False

    def rect(self):
        if not self.exploding:
            # During flight: 16x12 hitbox (cutting out the top 2 and bottom 2 pixels)
            return pygame.Rect(
                self.pos[0] - self.size[0] // 2,
                self.pos[1] - self.size[1] // 2 + 2,  # Adjust to cut top and bottom
                self.size[0],
                self.size[1] - 4  # Reduce height by 4 pixels (2 top, 2 bottom)
            )
        else:
            # During explosion: 16x16 hitbox
            return pygame.Rect(
                self.pos[0] - self.size[0] // 2,
                self.pos[1] - self.size[1] // 2,
                self.size[0],
                self.size[1]
            )

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        # Draw the projectile image
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, self.vertical_flip), (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

        # Draw the hitbox for debugging
        hitbox = self.rect().move(-offset[0], -offset[1])
        pygame.draw.rect(surf, (0, 255, 0), hitbox, 1)  # Green hitbox for visibility




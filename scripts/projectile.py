import pygame

class Projectile:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0, size=None):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['projectiles/' + p_type].copy()
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
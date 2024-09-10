import pygame
import random

class Rain:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed
        self.pos[1] -= self.speed - 5

    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))

class Raindrops:
    def __init__(self, rain_imgs, count = 16):
        self.raindrops = []

        for i in range(count):
            self.raindrops.append(Rain((random.random() * 99999, random.random() * 99999), random.choice(rain_imgs), -6, random.random() * 0.6 + 0.2))

        self.raindrops.sort(key=lambda x: x.depth)

    def update(self):
        for raindrop in self.raindrops:
            raindrop.update()

    def render(self, surf, offset=(0, 0)):
        for raindrops in self.raindrops:
            raindrops.render(surf, offset=offset)
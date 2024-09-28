import pygame
import random
import math

class Precipitation:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self, precipitation_type):
        if precipitation_type == 'rain':
            self.pos[0] += self.speed
            self.pos[1] -= self.speed
        elif precipitation_type == 'snow':
            # Use a sine function to oscillate horizontally
            # 'self.pos[1]' acts as the input to the sin function (affecting the x position)
            sway_amplitude = 0.5  # How far snow can sway from side to side
            sway_frequency = 0.05  # How quickly it sways back and forth

            # Adjust x-position based on the sin of the y-position (creating back-and-forth motion)
            self.pos[0] += sway_amplitude * math.sin(self.pos[1] * sway_frequency)
            self.pos[1] -= self.speed  # Continue falling downward

    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))

class Raindrops():
    def __init__(self, rain_imgs, count = 16):
        self.raindrops = []
        self.precipitation_type = 'rain'

        for i in range(count):
            self.raindrops.append(Precipitation((random.random() * 99999, random.random() * 99999), random.choice(rain_imgs), -5, random.random() * 0.6 + 0.2))

        self.raindrops.sort(key=lambda x: x.depth)

    def update(self,):
        for raindrop in self.raindrops:
            raindrop.update(self.precipitation_type)

    def render(self, surf, offset=(0, 0)):
        for raindrops in self.raindrops:
            raindrops.render(surf, offset=offset)

class Snow():
    def __init__(self, snow_imgs, count = 16):
        self.snowflakes = []
        self.precipitation_type = 'snow'

        for i in range(count):
            self.snowflakes.append(Precipitation((random.random() * 99999, random.random() * 99999), random.choice(snow_imgs), -1, random.random() * 0.6 + 0.2))

        self.snowflakes.sort(key=lambda x: x.depth)

    def update(self):
        for snowflake in self.snowflakes:
            snowflake.update(self.precipitation_type)

    def render(self, surf, offset=(0, 0)):
        for snowflake in self.snowflakes:
            snowflake.render(surf, offset=offset)
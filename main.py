import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.particle import Particle


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Draconic Isles")
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()

        self.movement_x = [False, False]
        self.movement_y = [False, False]

        self.assets = {
            'player': load_image('player/player.png'),
            'walls': load_images('walls/'),
            'player/idle_down': Animation(load_images('player/idle/idle_down'), img_dur=25),
            'player/idle_up': Animation(load_images('player/idle/idle_up'), img_dur=25),
            'player/walking': Animation(load_images('player/walking'), img_dur=5),
        }

    def main(self):
        # Initialize game objects --------------------------------------------------------------------------------------------------------------------------------
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load()
        all_tiles = self.tilemap.get_all_tiles()
        self.player = Player(self, (self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size), (16, 8))

        self.scroll = [self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size]

        # Main Game Loop -----------------------------------------------------------------------------------------------------------------------------------------
        while True:
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.display.fill((200, 200, 255))  

            # Update objects
            self.player.update(self.movement_x, self.movement_y)
            
            # RENDERING----------------------------------------------------------------------------------------------------------------------------------------------
            # Collect all tiles and objects to be rendered
            render_objects = []

            # Add all tiles from the tilemap
            for tile in all_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                render_objects.append((tile, tile_pos[1]))

            # Add player to render list
            render_objects.append((self.player, self.player.pos[1]))

            # Sort all render objects by their y-coordinate (top-down order)
            render_objects.sort(key=lambda obj: obj[1])

            # Render all objects in sorted order
            for obj, _ in render_objects:
                if isinstance(obj, Player):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, dict):
                    # Render the tile using the abstracted method
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)
            
            # EVENT HANDLING-----------------------------------------------------------------------------------------------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement_x[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement_x[1] = True
                    if event.key == pygame.K_UP:
                        self.movement_y[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement_y[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement_x[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement_x[1] = False
                    if event.key == pygame.K_UP:
                        self.movement_y[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement_y[1] = False

            # Update the display
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)


Game().main()



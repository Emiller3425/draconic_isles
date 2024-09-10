import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.particle import Particle
from scripts.lantern import Lantern
from scripts.ui import UI
from scripts.rain import Rain, Raindrops


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Draconic Isles")
        self.screen = pygame.display.set_mode((640, 480))
        self.screen.fill((0, 0, 0))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()

        self.movement_x = [False, False]
        self.movement_y = [False, False]

        self.assets = {
            'player': load_image('player/player.png'),
            'skeleton': load_image('skeleton/skeleton.png'),
            'walls': load_images('walls/'),
            'ground': load_images('ground/'),
            'lantern': load_images('lantern/'),
            'tree': load_images('tree/'),
            'bush': load_images('bush/'),
            'player/idle_down': Animation(load_images('player/idle/idle_down'), img_dur=25),
            'player/idle_up': Animation(load_images('player/idle/idle_up'), img_dur=25),
            'player/idle_horizontal': Animation(load_images('player/idle/idle_horizontal'), img_dur=25),
            'player/walking_down': Animation(load_images('player/walking/walking_down'), img_dur=4),
            'player/walking_up': Animation(load_images('player/walking/walking_up'), img_dur=4),
            'player/walking_horizontal': Animation(load_images('player/walking/walking_horizontal'), img_dur=8),
            'skeleton/idle_down': Animation(load_images('skeleton/idle/idle_down'), img_dur=25),
            'skeleton/idle_up': Animation(load_images('skeleton/idle/idle_up'), img_dur=25),
            'skeleton/idle_horizontal': Animation(load_images('skeleton/idle/idle_horizontal'), img_dur=25),
            'skeleton/walking_down': Animation(load_images('skeleton/walking/walking_down'), img_dur=4),
            'skeleton/walking_up': Animation(load_images('skeleton/walking/walking_up'), img_dur=4),
            'skeleton/walking_horizontal': Animation(load_images('skeleton/walking/walking_horizontal'), img_dur=8),
            'attribute_bar': load_image('ui/attribute_bar.png'),
        }

        # List for deferred rendering
        self.deferred_tiles = []
        self.rain_particles = Raindrops(load_images('rain/'), count = 140)

    def main(self):
        # Initialize tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load()
        all_tiles = self.tilemap.get_all_ordered_tiles()
        non_ordered_tiles = self.tilemap.get_all_non_ordered_tiles()

        # Initialize player
        self.player = Player(self, (self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size), (16, 6))
        # Initialize scroll
        self.scroll = [self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size]

        self.enemies = []
        for pos in self.tilemap.enemy_positions:
            self.enemies.append(Enemy(self, (pos[0] * self.tilemap.tile_size, pos[1] * self.tilemap.tile_size), (16, 6)))

        self.ui = UI(self, self.player)

        # Get all lanterns
        self.lanterns = []
        for lantern in self.tilemap.extract([('lantern', 0)], keep=True):
            self.lanterns.append(Lantern(self, lantern['pos']))

        # Main Game Loop
        while True:
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.display.fill((0, 0, 0))

            # Update objects
            self.player.update(self.movement_x, self.movement_y)

            for enemy in self.enemies:
                enemy.update((0, 0), (0, 0.2))
                enemy.render(self.display, offset=render_scroll)
            
            # RENDERING
            # Collect all tiles and objects to be rendered
            render_order_objects = []
            render_objects = []

            # Add all tiles from the tilemap
            for tile in all_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                render_order_objects.append((tile, tile_pos[1]))
            
            for tile in non_ordered_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                render_objects.append((tile, tile_pos[1]))

            # Add player to render list
            render_order_objects.append((self.player, self.player.pos[1]))

            # Add enemies to render list
            for enemy in self.enemies:
                render_order_objects.append((enemy, enemy.pos[1]))

            # Sort all render objects by their y-coordinate (top-down order)
            render_order_objects.sort(key=lambda obj: obj[1])

            # Render all non-ordered tiles first
            for obj, _ in render_objects:
                self.tilemap.render_tile(self.display, obj, offset=render_scroll)

            # Render all objects in sorted order
            for obj, _ in render_order_objects:
                if isinstance(obj, Player):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Enemy):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, dict):
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)
            
            # Render deferred tiles (tree tops) to ensure they are above the player
            self.tilemap.render_deferred_tiles()
            
            # Recreate the night overlay for this frame
            night_overlay = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
            night_overlay.fill((0, 0, 0, 150))  # Recreate the night effect with alpha 150

            # Render the lanterns to remove the night effect in their vicinity
            for lantern in self.lanterns:
                lantern.render(night_overlay, offset=render_scroll)

            # Apply the night overlay effect after rendering everything
            self.display.blit(night_overlay, (0, 0))

            self.rain_particles.update()
            self.rain_particles.render(self.display, offset=render_scroll)

            # Render the UI on top of everything
            self.ui.render(self.display)

            # EVENT HANDLING
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
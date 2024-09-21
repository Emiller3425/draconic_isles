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
from scripts.projectile import Projectile, FireballSpell


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Draconic Isles")
        self.screen = pygame.display.set_mode((960, 720))
        self.screen.fill((0, 0, 0))
        self.display = pygame.Surface((480, 320), pygame.SRCALPHA)
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
            'player_attribute_bar': load_image('ui/player_attribute_bar.png'),
            'minor_enemy_health_bar': load_image('ui/minor_enemy_health_bar.png'),
            'equipped_melee_card' : load_image('ui/equipped_melee_card.png'),
            'equipped_spell_card' : load_image('ui/equipped_spell_card.png'),
            'basic_sword' : load_image('weapons/swords/basic_sword.png'),
            'fireball' : load_image('spells/damage/fireball/fireball.png'),
            'fireballspell_horizontal' : Animation(load_images('spells/damage/fireball/traveling_horizontal'), img_dur=8),
            'fireballspell_vertical' : Animation(load_images('spells/damage/fireball/traveling_vertical'), img_dur=8),
            'fireballspell_impact' : Animation(load_images('spells/damage/fireball/impact'), img_dur=2),
        }


        # List for deferred rendering
        self.deferred_tiles = []
        self.rain_particles = Raindrops(load_images('rain/'), count=140)

    def trigger_flash(self, duration=80):
        self.flash_duration = duration
        self.flash_alpha = 150  # Maximum opacity at the start

    def main(self):
        # Initialize tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load()
        self.all_tiles = self.tilemap.get_all_ordered_tiles()
        self.non_ordered_tiles = self.tilemap.get_all_non_ordered_tiles()

        # Night overlay effect
        self.night_overlay = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.night_overlay.fill((0, 0, 0, 150))  # Recreate the night effect with alpha 150

        # Flash(lightning) effect 
        self.flash_alpha = 0  # Initial alpha value for the flash effect
        self.flash_duration = 0  # Duration of the flash effect
        self.flash_surface = pygame.Surface(self.display.get_size())  # Surface for the flash effect
        self.flash_surface.fill((255, 255, 255))  # White flash effect

        # Initialize player
        self.player = Player(self, (self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size), (16, 6))
        # Initialize scroll
        self.scroll = [self.tilemap.player_position[0] * self.tilemap.tile_size, self.tilemap.player_position[1] * self.tilemap.tile_size]

        self.enemies = []
        for pos in self.tilemap.enemy_positions:
            self.enemies.append(Enemy(self, (pos[0] * self.tilemap.tile_size, pos[1] * self.tilemap.tile_size), (16, 6)))

        self.ui = UI(self, self.player, self.player.equipped_melee, self.player.equipped_spell)

        # Get all lanterns
        self.lanterns = []
        for lantern in self.tilemap.extract([('lantern', 0)], keep=True):
            self.lanterns.append(Lantern(self, lantern['pos']))

        # Get all projectiles
        self.projectiles = []

        # Main Game Loop
        while True:
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.display.fill((0, 0, 0))

            # Update objects
            self.player.update(self.movement_x, self.movement_y)

            for enemy in self.enemies:
                enemy.update()
                enemy.render(self.display, offset=render_scroll)
            
            # RENDERING
            # Collect all tiles and objects to be rendered
            self.render_order_objects = []
            self.render_objects = []

            # Add all tiles from the tilemap
            for tile in self.all_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                self.render_order_objects.append((tile, tile_pos[1]))
            
            for tile in self.non_ordered_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                self.render_objects.append((tile, tile_pos[1]))

            # Add player to render list
            self.render_order_objects.append((self.player, self.player.pos[1]))

            # Add enemies to render list
            for enemy in self.enemies:
                self.render_order_objects.append((enemy, enemy.pos[1]))

            # Sort all render objects by their y-coordinate (top-down order)
            self.render_order_objects.sort(key=lambda obj: obj[1])

            # Render all non-ordered tiles first
            for obj, _ in self.render_objects:
                self.tilemap.render_tile(self.display, obj, offset=render_scroll)

            # Render all objects in sorted order
            for obj, _ in self.render_order_objects:
                if isinstance(obj, Player):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Enemy):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, dict):
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)
            
            # Render deferred tiles (tree tops) to ensure they are above the player
            self.tilemap.render_deferred_tiles()
            
            # Recreate the night overlay for this frame
            self.night_overlay = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
            self.night_overlay.fill((0, 0, 0, 150))  # Recreate the night effect with alpha 150

            for projectile in self.projectiles[:]:
                if projectile.update():  # If the projectile should be removed
                    self.projectiles.remove(projectile)
                else:
                    projectile.render(self.display, offset=render_scroll)

            # Render the lanterns to remove the night effect in their vicinity
            for lantern in self.lanterns:
                lantern.render(self.night_overlay, offset=render_scroll)

            # Apply the night overlay effect after rendering everything
            self.display.blit(self.night_overlay, (0, 0))

            self.rain_particles.update()
            self.rain_particles.render(self.display, offset=render_scroll)

            # Render the UI on top of everything
            self.ui.render(self.display, render_scroll)

            # Chance to trigger a flash effect
            if random.random() < 0.0005:
                self.trigger_flash()

            # Update flash effect if active
            if self.flash_duration > 0:
                self.flash_duration -= 1
                self.flash_alpha = max(0, int(self.flash_alpha * 0.98)) # Fade out over time
                self.flash_surface.set_alpha(self.flash_alpha)
                self.display.blit(self.flash_surface, (0, 0))

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
                    if event.key == pygame.K_q:
                        self.player.melee()
                    if event.key == pygame.K_e:  # Cast fireball spell when 'E' is pressed
                        self.player.cast_spell()
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

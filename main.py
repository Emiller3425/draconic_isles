import pygame
import sys
import random
import math
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.tilemap import Tilemap
from scripts.particle import Particle
from scripts.light import Light
from scripts.ui import UI
from scripts.precipitation import Precipitation, Raindrops
from scripts.projectile import Projectile, FireballSpell
from scripts.weather import Weather
from scripts.bonfire import Bonfire
from scripts.animated import Animated
from scripts.drop import Drop


class Game:
    def __init__(self):

        pygame.init()

        pygame.display.set_caption("Draconic Isles")
        self.screen = pygame.display.set_mode((720, 600))
        self.screen.fill((0, 0, 0))
        self.display = pygame.Surface((360, 280), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()

        self.movement_x = [False, False]
        self.movement_y = [False, False]

        self.assets = {
            'title_screen': load_image('screens/title_screen.png'),
            'player': load_images('player/'),
            'skeleton': load_images('skeleton/'),
            'walls': load_images('walls/'),
            'ground': load_images('ground/'),
            'light': load_images('light/'),
            'tree': load_images('tree/'),
            'tree/animation' :  Animation(load_images('tree/animation'), img_dur=60),
            'bridge': load_images('bridge'),
            'bush': load_images('bush/'),
            'bush/animation' :  Animation(load_images('bush/animation'), img_dur=30),
            'rock': load_images('rock/'),
            'red_flower' : load_images('flowers/red_flower'),
            'red_flower/animation' :  Animation(load_images('flowers/red_flower/animation'), img_dur=30),
            'purple_flower' : load_images('flowers/purple_flower'),
            'purple_flower/animation' :  Animation(load_images('flowers/purple_flower/animation'), img_dur=30),
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
            'soul_counter_card' : load_image('ui/soul_counter_card.png'),
            'basic_sword' : load_image('weapons/swords/basic_sword/basic_sword.png'),
            'basic_sword_vertical' : load_image('weapons/swords/basic_sword/basic_sword_vertical.png'),
            'basic_sword_horizontal' : load_image('weapons/swords/basic_sword/basic_sword_horizontal.png'),
            'fireball' : load_image('spells/damage/fireball/fireball.png'),
            'fireballspell_horizontal' : Animation(load_images('spells/damage/fireball/traveling_horizontal'), img_dur=8),
            'fireballspell_vertical' : Animation(load_images('spells/damage/fireball/traveling_vertical'), img_dur=8),
            'fireballspell_impact' : Animation(load_images('spells/damage/fireball/impact'), img_dur=2),
            'particles/lamp_particle': Animation(load_images('particles/lamp_particle/'), img_dur=10, loop=False),
            'particles/smoke_particle': Animation(load_images('particles/smoke_particle/'), img_dur=40, loop=False),
            'bonfire': load_images('bonfire/'),
            'bonfire/animation': Animation(load_images('bonfire/animation'), img_dur=8),
            'water': load_images('water/'),
            'water/animation' : Animation(load_images('water/animation'), img_dur=10),
            'lava': load_images('lava/'),
            'lava/animation' : Animation(load_images('lava/animation'), img_dur=20),
            'f_key': load_image('keys/f_key/0.png'),
            'digits' : load_images('digits')
        }


        # List for deferred rendering
        self.deferred_tiles = []
        # self.rain_particles = Raindrops(load_images('rain/'), count=140)

    # def trigger_lighting(self, duration=80):
    #     self.flash_duration = duration
    #     self.flash_alpha = 150  # Maximum opacity at the start

    def main(self):
        # Initialize tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load()
        self.all_tiles = self.tilemap.get_all_ordered_tiles()
        self.non_ordered_tiles = self.tilemap.get_all_non_ordered_tiles()

        # Night overlay effect
        self.night_overlay = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.weather_system = Weather(self)
        # self.night_overlay.fill((0, 0, 0, 150))  # Recreate the night effect with alpha 150

        # Flash(lightning) effect 
        # self.flash_alpha = 0  # Initial alpha value for the flash effect
        # self.flash_duration = 0  # Duration of the flash effect
        # self.flash_surface = pygame.Surface(self.display.get_size())  # Surface for the flash effect
        # self.flash_surface.fill((255, 255, 255))  # White flash effect

        # Enemies
        self.enemies = []
        # Bonfires
        self.bonfires = []
        # Y-sorted animatied objects
        self.animated_physics_objects = []
        # Rendred first animated objects
        self.animated_objects = []
        # lights
        self.lights = []
        # lamp particle spawners
        self.lamp_particle_spawners = []
        # smoke particle spawners
        self.smoke_particle_spawners = []
        # Get all projectiless
        self.projectiles = []
        # Get Particles
        self.particles = []
        # drops
        self.drops = []

        # Animated physics objects
        for k in self.tilemap.object_layers:
            for v in self.tilemap.object_layers[k]['positions']:
                if k == 'player':
                    self.player = Player(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), (12, 14), (14, 6))
                    self.scroll = [v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size]
                elif k == 'skeleton':
                    self.enemies.append(Enemy(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), (14, 16), (14, 6)))
                elif k =='bonfire':
                    self.bonfires.append(Bonfire(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size)))
                else:
                    self.animated_physics_objects.append(Animated(self, k, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), frame = 0))
        # Animated objects
        for k in self.tilemap.animated_layers:
            for v in self.tilemap.animated_layers[k]['positions']:
                if 'flower' in k:
                    self.animated_objects.append(Animated(self, k, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), frame = random.randint(0, len(self.assets[k+'/animation'].images))))
                else:
                    self.animated_objects.append(Animated(self, k, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), frame = 0))
                if k =='lava':
                    self.lights.append(Light(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), 25, [70, 20, 0]))

                    

        self.ui = UI(self, self.player, self.player.equipped_melee, self.player.equipped_spell)

        # Get all light objects
        for light in self.tilemap.extract([('light', 0)], keep=True):
            self.lights.append(Light(self, light['pos'], 20, [20, 20, 0]))
            self.lamp_particle_spawners.append(pygame.rect.Rect(light['pos'][0], light['pos'][1], 16, 16))
        
        for bonfire in self.bonfires:
            self.smoke_particle_spawners.append(pygame.rect.Rect(bonfire.pos[0] + 8, bonfire.pos[1] - 18, 16, 16))

        # Main Game Loop
        while True:
            self.scroll[0] += (self.player.physics_rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.physics_rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.display.fill((0, 0, 0))

            # Update objects
            self.player.update(self.movement_x, self.movement_y)

            for enemy in self.enemies:
                enemy.update()

            for bonfire in self.bonfires:
                bonfire.update()

            for animated in self.animated_objects:
                animated.update()

            for animated in self.animated_physics_objects:
                animated.update()
            
            
            # RENDERING
            # Collect all tiles and objects to be rendered
            self.render_order_objects = []
            self.render_objects = []

            # Add y-ordered tiles to ordered render list
            for tile in self.all_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                self.render_order_objects.append((tile, tile_pos[1]))
            
            # Add tiles to always be rendered first to list
            for tile in self.non_ordered_tiles:
                tile_pos = (tile['pos'][0] * self.tilemap.tile_size, tile['pos'][1] * self.tilemap.tile_size)
                self.render_objects.append((tile, tile_pos[1]))

            # Add player to render list
            self.render_order_objects.append((self.player, self.player.pos[1] - 8))

            # Add enemies to render list
            for enemy in self.enemies:
                self.render_order_objects.append((enemy, enemy.pos[1] - 8))

            for bonfire in self.bonfires:
                self.render_order_objects.append((bonfire, bonfire.pos[1]))

            for projectile in self.projectiles[:]:
                if projectile.update():  # If the projectile should be removed
                    self.projectiles.remove(projectile)
                else:
                    self.render_order_objects.append((projectile, projectile.pos[1]))
            
            for animated in self.animated_physics_objects:
                self.render_order_objects.append((animated, animated.pos[1]))

            # Sort all render objects by their y-coordinate (top-down order)
            self.render_order_objects.sort(key=lambda obj: obj[1])

            # Render all non-ordered tiles not bridge
            for obj, _ in self.render_objects:
                if obj['type'] != 'bridge':
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)

            # render animated objects
            for animated in self.animated_objects:
                animated.render(self.display, offset=render_scroll)

            # render bridges
            for obj, _ in self.render_objects:
                if obj['type'] == 'bridge':
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)

            # Render all objects in sorted order
            for obj, _ in self.render_order_objects:
                if isinstance(obj, Player):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Enemy):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Projectile):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Bonfire):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Animated):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, dict):
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)

            # Render Interact Key Floater
            for bonfire in self.player.nearby_bonfire_objects:
                bonfire.render_interact(self.display, offset=render_scroll)

            
            
            # update weather system
            self.weather_system.update()
            self.weather_system.render(self.display, offset=(0, 0))

            # for projectile in self.projectiles[:]:
            #     if projectile.update():  # If the projectile should be removed
            #         self.projectiles.remove(projectile)
            #     else:
            #         projectile.render(self.display, offset=render_scroll)

            # Render the lanterns to remove the night effect in their vicinity
            for light in self.lights:
                light.render(self.night_overlay, offset=render_scroll)
            
            # TODO - Add particle behavior
            for rect in self.lamp_particle_spawners:
                if random.random() < 0.002:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'lamp_particle', pos, velocity=[-0.15, 0.3], frame=random.randint(0, 10)))

            for rect in self.smoke_particle_spawners:
                if random.random() < 0.5:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'smoke_particle', pos, velocity=[0, -0.2], frame=random.randint(0, 10)))


            # animate and render particles
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if isinstance(particle, Particle) and particle.type == 'lamp_particle':
                    particle.pos[0] += math.sin(random.random()) * 0.3
                    particle.pos[1] += math.sin(random.random()) * 0.3
                elif isinstance(particle, Particle) and particle.type == 'smoke_particle':
                     particle.pos[0] += math.sin(random.random()) * 0.7 * random.randint(-1, 1)
                if kill:
                    self.particles.remove(particle)


            # Apply the night overlay effect after rendering everything
            self.display.blit(self.night_overlay, (0, 0))

            # Render the UI on top of everything
            self.ui.render(self.display, render_scroll)

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
                    if event.key == pygame.K_e: 
                        self.player.cast_spell()
                    # TODO bonfire interact
                    if event.key == pygame.K_f:
                        self.player.rest_at_bonfire()
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
            # title screen
            # self.screen.blit(pygame.transform.scale(self.assets['title_screen'], self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)


Game().main()

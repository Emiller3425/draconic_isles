import pygame
import sys
import random
import math
import json
import os

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
from scripts.chest import Chest


class Game:
    def __init__(self):

        pygame.init()

        pygame.display.set_caption("Draconic Isles")
        self.screen = pygame.display.set_mode((720, 600))
        self.screen.fill((0, 0, 0))
        self.display = pygame.Surface((360, 280), pygame.SRCALPHA)
        self.upgrade_screen_display = pygame.Surface((360, 280), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.show_start_screen = True
        self.show_upgrade_screen = False

        self.movement_x = [False, False]
        self.movement_y = [False, False]

        self.assets = {
            # title screen assets
            'title_screen': load_image('screens/title_screen/0.png'),
            'title_screen/animation': Animation(load_images('screens/title_screen/animation'), img_dur = 7),
            'continue_button': load_image('screens/buttons/continue_button/0.png'),
            'continue_button_hover' : load_image('screens/buttons/continue_button/1.png'),
            'continue_button_greyed_out' : load_image('screens/buttons/continue_button/2.png'),
            'new_game_button': load_image('screens/buttons/new_game_button/0.png'),
            'new_game_button_hover': load_image('screens/buttons/new_game_button/1.png'),
            # upgrade screen
            'upgrade_screen' : load_image('screens/upgrade_screen/0.png'),
            # player
            'player': load_images('player/'),
            # skeleton
            'skeleton': load_images('skeleton/'),
            # wall types
            'walls': load_images('walls/'),
            # ground types
            'ground': load_images('ground/'),
            # lights
            'light': load_images('light/'),
            # trees
            'tree': load_images('tree/'),
            'tree/animation' :  Animation(load_images('tree/animation'), img_dur=60),
            # bridges
            'bridge': load_images('bridge'),
            # bushes
            'bush': load_images('bush/'),
            'bush/animation' :  Animation(load_images('bush/animation'), img_dur=30),
            # rocks
            'rock': load_images('rock/'),
            # flowers
            'red_flower' : load_images('flowers/red_flower'),
            'red_flower/animation' :  Animation(load_images('flowers/red_flower/animation'), img_dur=30),
            'purple_flower' : load_images('flowers/purple_flower'),
            'purple_flower/animation' :  Animation(load_images('flowers/purple_flower/animation'), img_dur=30),
            # player animations
            'player/idle_down': Animation(load_images('player/idle/idle_down'), img_dur=25),
            'player/idle_up': Animation(load_images('player/idle/idle_up'), img_dur=25),
            'player/idle_horizontal': Animation(load_images('player/idle/idle_horizontal'), img_dur=25),
            'player/walking_down': Animation(load_images('player/walking/walking_down'), img_dur=4),
            'player/walking_up': Animation(load_images('player/walking/walking_up'), img_dur=4),
            'player/walking_horizontal': Animation(load_images('player/walking/walking_horizontal'), img_dur=8),
            # sekelton animations
            'skeleton/idle_down': Animation(load_images('skeleton/idle/idle_down'), img_dur=25),
            'skeleton/idle_up': Animation(load_images('skeleton/idle/idle_up'), img_dur=25),
            'skeleton/idle_horizontal': Animation(load_images('skeleton/idle/idle_horizontal'), img_dur=25),
            'skeleton/walking_down': Animation(load_images('skeleton/walking/walking_down'), img_dur=4),
            'skeleton/walking_up': Animation(load_images('skeleton/walking/walking_up'), img_dur=4),
            'skeleton/walking_horizontal': Animation(load_images('skeleton/walking/walking_horizontal'), img_dur=8),
            # UI
            'player_attribute_bar': load_image('ui/player_attribute_bar.png'),
            'minor_enemy_health_bar': load_image('ui/minor_enemy_health_bar.png'),
            'equipped_melee_card' : load_image('ui/equipped_melee_card.png'),
            'equipped_spell_card' : load_image('ui/equipped_spell_card.png'),
            'soul_counter_card' : load_image('ui/soul_counter_card.png'),
            # basic sword
            'basic_sword' : load_image('weapons/swords/basic_sword/basic_sword.png'),
            'basic_sword_vertical' : load_image('weapons/swords/basic_sword/basic_sword_vertical.png'),
            'basic_sword_horizontal' : load_image('weapons/swords/basic_sword/basic_sword_horizontal.png'),
            # fireball
            'fireball' : load_image('spells/damage/fireball/fireball.png'),
            'fireballspell_horizontal' : Animation(load_images('spells/damage/fireball/traveling_horizontal'), img_dur=8),
            'fireballspell_vertical' : Animation(load_images('spells/damage/fireball/traveling_vertical'), img_dur=8),
            'fireballspell_impact' : Animation(load_images('spells/damage/fireball/impact'), img_dur=2),
            # particles
            'particles/lamp_particle': Animation(load_images('particles/lamp_particle/'), img_dur=10, loop=False),
            'particles/smoke_particle': Animation(load_images('particles/smoke_particle/'), img_dur=40, loop=False),
            'particles/soul_particle' : Animation(load_images('particles/soul_particle/'), img_dur=40, loop=False),
            #bonfire
            'bonfire': load_images('bonfire/'),
            'bonfire/animation': Animation(load_images('bonfire/animation'), img_dur=8),
            # water
            'water': load_images('water/'),
            'water/animation' : Animation(load_images('water/animation'), img_dur=10),
            # lava
            'lava': load_images('lava/'),
            'lava/animation' : Animation(load_images('lava/animation'), img_dur=20),
            # keys
            'f_key': load_image('keys/f_key/0.png'),
            # digits
            'grey_digits' : load_images('digits/grey_digits'),
            'red_digits' : load_images('digits/red_digits'),
            'green_digits' : load_images('digits/green_digits'),
            'blue_digits' : load_images('digits/blue_digits'),
            # dropped souls
            'dropped_souls' : load_image('drops/souls/0.png'),
            # upgrade arrows
            'upgrade_arrow' : load_image('ui/arrows/upgrade_arrow/upgrade_arrow.png'),
            'upgrade_arrow_hover' : load_image('ui/arrows/upgrade_arrow/upgrade_arrow_hover.png'),
            'upgrade_arrow_greyed_out' : load_image('ui/arrows/upgrade_arrow/upgrade_arrow_greyed_out.png'),
            # downgrade arrows
            'downgrade_arrow' : load_image('ui/arrows/downgrade_arrow/downgrade_arrow.png'),
            'downgrade_arrow_hover' : load_image('ui/arrows/downgrade_arrow/downgrade_arrow_hover.png'),
            'downgrade_arrow_greyed_out' : load_image('ui/arrows/downgrade_arrow/downgrade_arrow_greyed_out.png'),
            # confirm button
            'confirm_button' : load_image('screens/buttons/confirm_button/confirm_button.png'),
            'confirm_button_hover' : load_image('screens/buttons/confirm_button/confirm_button_hover.png'),
            'confirm_button_greyed_out' : load_image('screens/buttons/confirm_button/confirm_button_greyed_out.png'),
            # next level ui piece
            'next_level' : load_image('ui/next_level.png'),
            # chests
            'bronze_chest' : load_image('bronze_chest/0.png'),
            'silver_chest' : load_image('silver_chest/0.png'),
            'gold_chest' : load_image('gold_chest/0.png'),
            'bronze_chest_animation' : Animation(load_images('bronze_chest/animation/'), img_dur=5, loop=False),
            'silver_chest_animation' : Animation(load_images('silver_chest/animation/'), img_dur=5, loop=False),
            'gold_chest_animation' : Animation(load_images('gold_chest/animation/'), img_dur=5, loop=False),
        }
        self.audio = {
            # TODO audio lol retard
        }


        # List for deferred rendering
        self.deferred_tiles = []
        # self.rain_particles = Raindrops(load_images('rain/'), count=140)

    # def trigger_lighting(self, duration=80):
    #     self.flash_duration = duration
    #     self.flash_alpha = 150  # Maximum opacity at the start

    def run(self):
        while True:
            if self.show_start_screen:
                self.start_screen() 
            else:
                self.main()

    # Handles all logic in the start screen when the game is initially booted up
    # TODO Any enemies that dies need to be readded to this array
    def reset_enemies(self):
        self.enemies.clear()
        for k in self.tilemap.object_layers:
            for v in self.tilemap.object_layers[k]['positions']:
                if k == 'skeleton':
                    self.enemies.append(Enemy(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), (14, 16), (14, 6)))
            

    def fade_out(self):
        self.show_upgrade_screen = True
        pass

    # TODO: Add general pause screen when at bonfires to enable fast travel
    def upgrade_screen(self):

        current_level = self.player.level
        current_souls = self.player.souls
        current_health = self.player.max_health
        current_stamina = self.player.stamina
        current_mana = self.player.mana
        
        # upgrade arrows
        upgrade_health_arrow_rect = pygame.Rect(450, 140, 50, 50)
        upgrade_stamina_arrow_rect = pygame.Rect(450, 260, 50, 50)
        upgrade_mana_arrow_rect = pygame.Rect(450, 380, 50, 50)

        # downgrade arrows
        downgrade_health_arrow_rect = pygame.Rect(520, 140, 50, 50)
        downgrade_stamina_arrow_rect = pygame.Rect(520, 260, 50, 50)
        downgrade_mana_arrow_rect = pygame.Rect(520, 380, 50, 50)

        # confirm button
        confirm_button_rect = pygame.Rect(520, 500, 100, 50)
        
        # for downgrade level logic while applying levels
        health_levels_applied = 0
        stamina_levels_applied = 0
        mana_levels_applied = 0

        while True:
            self.screen.blit(pygame.transform.scale(self.assets['upgrade_screen'], (self.screen.get_width() - 200, self.screen.get_height() - 200)), (100,100))
            cursor_pos = pygame.mouse.get_pos()
            # Conditions for handling button_states based on cursor positions
            if True:
                # keep reugular UI on screen
                self.ui.render(self.display, self.player)
                self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

                # Upgrade Screen
                self.screen.blit(pygame.transform.scale(self.assets['upgrade_screen'], (self.screen.get_width() - 200, self.screen.get_height() - 200)), (100,100))
                self.screen.blit(self.assets['next_level'], (400, 500))
                self.ui.render_next_level(self.screen, self.player.level),
                self.ui.render_health(self.screen, self.player)
                self.ui.render_stamina(self.screen, self.player)
                self.ui.render_mana(self.screen, self.player)
                if self.player.souls < self.player.level * 100:
                    can_add_level = False
                    self.screen.blit(self.assets['upgrade_arrow_greyed_out'], (450, 140))
                    self.screen.blit(self.assets['upgrade_arrow_greyed_out'], (450, 260))
                    self.screen.blit(self.assets['upgrade_arrow_greyed_out'], (450, 380))
                else:
                    can_add_level = True
                    # upgrade arrows
                    if upgrade_health_arrow_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['upgrade_arrow_hover'], (450, 140))
                    else:
                        self.screen.blit(self.assets['upgrade_arrow'], (450, 140))
                    if upgrade_stamina_arrow_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['upgrade_arrow_hover'], (450, 260))
                    else:
                        self.screen.blit(self.assets['upgrade_arrow'], (450, 260))
                    if upgrade_mana_arrow_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['upgrade_arrow_hover'], (450, 380))
                    else:
                        self.screen.blit(self.assets['upgrade_arrow'], (450, 380))
                # downgrade arrows
                if self.player.max_health > current_health:
                    if downgrade_health_arrow_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['downgrade_arrow_hover'], (520, 140))
                    else:
                        self.screen.blit(self.assets['downgrade_arrow'], (520, 140))
                else:
                    self.screen.blit(self.assets['downgrade_arrow_greyed_out'], (520, 140))
                if self.player.max_stamina > current_stamina:
                    if downgrade_stamina_arrow_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['downgrade_arrow_hover'], (520, 260))
                    else:
                        self.screen.blit(self.assets['downgrade_arrow'], (520, 260))
                else:
                    self.screen.blit(self.assets['downgrade_arrow_greyed_out'], (520, 260))
                if self.player.max_mana > current_mana:
                    if downgrade_mana_arrow_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['downgrade_arrow_hover'], (520, 380))
                    else:
                        self.screen.blit(self.assets['downgrade_arrow'], (520, 380))
                else:
                    self.screen.blit(self.assets['downgrade_arrow_greyed_out'], (520, 380))
                
                # Confirm Button
                if health_levels_applied > 0 or stamina_levels_applied > 0 or mana_levels_applied > 0:
                    if confirm_button_rect.collidepoint(cursor_pos):
                        self.screen.blit(self.assets['confirm_button_hover'], (520, 500))
                    else:
                        self.screen.blit(self.assets['confirm_button'], (520, 500))
                else:
                    self.screen.blit(self.assets['confirm_button_greyed_out'], (520, 500))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Handle Button Clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # upgrade arrows
                    if can_add_level:
                        if upgrade_health_arrow_rect.collidepoint(event.pos):
                            self.player.souls -= self.player.level * 100
                            self.player.max_health += 10
                            self.player.level += 1
                            health_levels_applied  += 1
                        if upgrade_stamina_arrow_rect.collidepoint(event.pos):
                            self.player.souls -= self.player.level * 100
                            self.player.max_stamina += 10
                            self.player.level += 1
                            stamina_levels_applied += 1
                        if upgrade_mana_arrow_rect.collidepoint(event.pos):
                            self.player.souls -= self.player.level * 100
                            self.player.max_mana += 10
                            self.player.level += 1
                            mana_levels_applied += 1
                    # downgrade arrows
                    if downgrade_health_arrow_rect.collidepoint(event.pos) and health_levels_applied > 0:
                        self.player.souls += (self.player.level - 1) * 100
                        self.player.max_health -= 10
                        self.player.level -= 1
                        health_levels_applied -= 1
                    if downgrade_stamina_arrow_rect.collidepoint(event.pos) and stamina_levels_applied > 0:
                        self.player.souls += (self.player.level - 1) * 100
                        self.player.max_stamina -= 10
                        self.player.level -= 1
                        stamina_levels_applied -= 1
                    if downgrade_mana_arrow_rect.collidepoint(event.pos) and mana_levels_applied > 0:
                        self.player.souls += (self.player.level - 1) * 100
                        self.player.max_mana -= 10
                        self.player.level -= 1
                        mana_levels_applied -= 1
                    pass

                    # confirm level-up handling
                    if confirm_button_rect.collidepoint(event.pos) and (health_levels_applied > 0 or stamina_levels_applied > 0 or mana_levels_applied > 0):
                        current_health = self.player.max_health
                        current_stamina = self.player.max_stamina
                        current_mana = self.player.max_mana
                        current_souls = self.player.souls
                        current_level = self.player.level
                        health_levels_applied = 0
                        stamina_levels_applied = 0
                        mana_levels_applied = 0

                        data = {
                        'max_health' : self.player.max_health,
                        'max_stamina' : self.player.max_stamina,
                        'max_mana' : self.player.max_mana,
                        'souls' : self.player.souls,
                        'equipped_melee' : self.player.equipped_melee,
                        'equipped_spell' : self.player.equipped_spell,
                        'spawn_point' : self.player.spawn_point,
                        'level' : self.player.level
                        }

                        with open('save_files/save.json', 'w') as save_file:
                            json.dump(data, save_file)
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.player.max_health = current_health
                        self.player.health = self.player.max_health
                        self.player.max_stamina = current_stamina
                        self.player.stamina = self.player.max_stamina
                        self.player.max_mana = current_mana
                        self.player.mana = self.player.max_mana
                        self.player.souls = current_souls
                        self.player.level = current_level
                        return
                    
            pygame.display.update()
            self.clock.tick(60)


    def start_screen(self):
        self.screen.fill((0, 0, 0))

        self.screen.blit(pygame.transform.scale(self.assets['title_screen'], self.screen.get_size()), (0,0))

        self.animation = self.assets['title_screen/animation']

        self.screen.blit(self.assets['new_game_button'], (self.screen.get_width() // 2 - self.assets['new_game_button'].get_width() // 2, 400))
        new_game_rect = pygame.Rect(self.screen.get_width() // 2 - self.assets['new_game_button'].get_width() // 2, 400, self.assets['new_game_button'].get_width(), self.assets['new_game_button'].get_height())

        self.screen.blit(self.assets['continue_button'], (self.screen.get_width() // 2 - self.assets['continue_button'].get_width() // 2, 450))
        continue_rect = pygame.Rect(self.screen.get_width() // 2 - self.assets['continue_button'].get_width() // 2, 450, self.assets['continue_button'].get_width(), self.assets['continue_button'].get_height())

        pygame.display.update()

        # TODO Fix handling for continue and new game when we get to end state
        while True:
            self.screen.blit(pygame.transform.scale(self.animation.img(), self.screen.get_size()), (0,0))
            cursor_pos = pygame.mouse.get_pos()
            if new_game_rect.collidepoint(cursor_pos):
                self.screen.blit(self.assets['new_game_button_hover'], (self.screen.get_width() // 2 - self.assets['new_game_button_hover'].get_width() // 2, 400))
            else:
                self.screen.blit(self.assets['new_game_button'], (self.screen.get_width() // 2 - self.assets['new_game_button'].get_width() // 2, 400))
            if os.path.isfile('save_files/save.json'):
                if continue_rect.collidepoint(cursor_pos):
                    self.screen.blit(self.assets['continue_button_hover'], (self.screen.get_width() // 2 - self.assets['continue_button_hover'].get_width() // 2, 450))
                else:
                    self.screen.blit(self.assets['continue_button'], (self.screen.get_width() // 2 - self.assets['continue_button'].get_width() // 2, 450))
            else:
                    self.screen.blit(self.assets['continue_button_greyed_out'], (self.screen.get_width() // 2 - self.assets['continue_button_greyed_out'].get_width() // 2, 450))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_rect.collidepoint(event.pos):
                        self.show_start_screen = False
                        self.continue_save = False
                        return
                    elif continue_rect.collidepoint(event.pos) and os.path.isfile('save_files/save.json'):
                        self.show_start_screen = False
                        self.continue_save = True
                        return
                    
            self.animation.update()
                    
            pygame.display.update()
            self.clock.tick(60)


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
        # chests
        self.chests = []
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
        # drop particle spawners
        self.drop_particle_spawners = []
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
                elif k == 'bronze_chest':
                    self.chests.append(Chest(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), 0))
                elif k == 'silver_chest':
                    self.chests.append(Chest(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), 1))
                elif k == 'gold_chest':
                    self.chests.append(Chest(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), 2))
                else:
                    self.animated_physics_objects.append(Animated(self, k, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), frame = 0))
        # Animated objects
        for k in self.tilemap.animated_layers:
            for v in self.tilemap.animated_layers[k]['positions']:
                if 'flower' in k:
                    self.animated_objects.append(Animated(self, k, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), frame = random.randint(0, len(self.assets[k+'/animation'].images))))
                else:
                    self.animated_objects.append(Animated(self, k, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), frame = 0))
                if k == 'lava':
                    self.lights.append(Light(self, (v[0] * self.tilemap.tile_size, v[1] * self.tilemap.tile_size), 25, [70, 20, 0]))

        # Save file information handling
        if self.continue_save:
            with open('save_files/save.json') as save_file:
                data = json.load(save_file)
                
            # Update player data based on JSON
            self.player.max_health = data['max_health']
            self.player.max_stamina = data['max_stamina']
            self.player.max_mana = data['max_mana']
            self.player.souls = data['souls']
            self.player.level = data['level']
            self.player.equipped_melee = data['equipped_melee']
            self.player.equipped_spell = data['equipped_spell']
            self.player.spawn_point = data['spawn_point']
            self.player.pos = self.player.spawn_point.copy()
        elif os.path.isfile('save_files/save.json'):
             os.remove('save_files/save.json')

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

            for chest in self.chests:
                if chest.is_opened:
                    chest.update()

            for animated in self.animated_objects:
                animated.update()

            for animated in self.animated_physics_objects:
                animated.update()

            for drop in self.drops:
                drop.update()
                if drop.has_particle_spawner == False:
                    drop.spawner = pygame.rect.Rect(drop.pos[0] - 4, drop.pos[1] - 8, 8, 8)
                    self.drop_particle_spawners.append(drop.spawner)
                    drop.has_particle_spawner = True
            
            
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
            
            for chest in self.chests:
                self.render_order_objects.append((chest, chest.pos[1]))

            for projectile in self.projectiles[:]:
                if projectile.update():  # If the projectile should be removed
                    self.projectiles.remove(projectile)
                else:
                    self.render_order_objects.append((projectile, projectile.pos[1]))
            
            for animated in self.animated_physics_objects:
                self.render_order_objects.append((animated, animated.pos[1]))

            for drop in self.drops:
                self.render_order_objects.append((drop, drop.original_pos[1] - 17))

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
                elif isinstance(obj, Chest):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Animated):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, Drop):
                    obj.render(self.display, offset=render_scroll)
                elif isinstance(obj, dict):
                    self.tilemap.render_tile(self.display, obj, offset=render_scroll)

            # Render Interact Key Floater
            for bonfire in self.player.nearby_bonfire_objects:
                bonfire.render_interact(self.display, offset=render_scroll)

             # Render Interact Key Floater
            for chest in self.player.nearby_chest_objects:
                chest.render_interact(self.display, offset=render_scroll)
            
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
            
            for rect in self.drop_particle_spawners:
                if random.random() < 0.25:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'soul_particle', pos, velocity=[0, -0.2], frame=random.randint(0, 10)))



            # animate and render particles
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if isinstance(particle, Particle) and particle.type == 'lamp_particle':
                    particle.pos[0] += math.sin(random.random()) * 0.3
                    particle.pos[1] += math.sin(random.random()) * 0.3
                elif isinstance(particle, Particle) and particle.type == 'smoke_particle':
                     particle.pos[0] += math.sin(random.random()) * 0.7 * random.randint(-1, 1)
                elif isinstance(particle, Particle) and particle.type == 'soul_particle':
                    particle.pos[0] += math.sin(random.uniform(-1,1)) 
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
                        if len(self.player.nearby_bonfire_objects)  >  0:
                            self.player.rest_at_bonfire()
                        if len(self.player.nearby_chest_objects) > 0:
                            self.player.open_chest()
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


Game().run()

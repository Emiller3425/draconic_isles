import pygame
import random
import math
import json

from scripts.precipitation import Raindrops, Precipitation, Snow
from scripts.utils import load_image, load_images, Animation


# TODO add a fog weather type, add a weather cycle that cycles through al types of weather, add particles for each type of precipitation, 

class Weather:
    def __init__(self, game, initial_weather_type='clear', day_duration=1000, night_duration=1000):
        self.game = game
        self.weather_type = initial_weather_type
        self.day_duration = day_duration
        self.night_duration = night_duration
        self.time = 0
        self.is_day = False  
        self.transitioning = False
        self.transition_time = 0
        self.transition_duration = 5000  # 10 seconds transition (assuming 60 FPS)
        self.night_overlay_opacity = 0 if self.is_day else 150  # Initial opacity based on time of day
        self.target_opacity = 150 if not self.is_day else 0 # Target opacity for transitions
        self.flash_alpha = 0
        self.flash_duration = 0
        self.rain = Raindrops(load_images('precipitation/rain'), count=100)
        self.heavy_rain = Raindrops(load_images('precipitation/rain'), count= 150)
        self.snow = Snow(load_images('precipitation/snow'), count=400)
        self.current_weather = 'clear' # 'clear', 'rain', 'thunderstorm', 'snow', 'fog

        self.night_overlay = pygame.Surface(self.game.display.get_size(), pygame.SRCALPHA)


    def update(self):
        # Update the time for day/night cycle
        self.time += 1
        if self.time >= self.day_duration and self.is_day:
            self.is_day = False
            self.time = 0
            self.start_transition(150)  # Start transitioning to night (opacity 150)
        elif self.time >= self.night_duration and not self.is_day:
            self.is_day = True
            self.time = 0
            self.start_transition(0)  # Start transitioning to day (opacity 10)

        # Update night overlay opacity if transitioning
        if self.transitioning:
            self.update_transition()

        # Handle weather-specific updates
        if self.current_weather == 'rain':
            self.raindrops.update()
        elif self.current_weather == 'thunderstorm':
            self.raindrops.update()
            self.update_thunderstorm()
        elif self.current_weather == 'snow':
            self.snow.update()

    def render(self, surf, offset=(0, 0)):
        # Render the rain if it's raining or thunderstorming
        if self.current_weather in ['rain', 'thunderstorm']:
            self.raindrops.render(surf, offset=offset)
        if self.current_weather == 'snow':
            self.snow.render(surf, offset=offset)

        # Render flash effect if in thunderstorm
        if self.current_weather == 'thunderstorm' and self.flash_duration > 0:
            self.flash_surface = pygame.Surface(self.game.display.get_size())
            self.flash_surface.fill((255, 255, 255))
            self.flash_surface.set_alpha(self.flash_alpha)
            surf.blit(self.flash_surface, (0, 0))

        # Update the night overlay based on the current opacity
        self.game.night_overlay.fill((0, 0, 0, self.night_overlay_opacity))
        surf.blit(self.night_overlay, (0, 0))

    def start_transition(self, target_opacity):
        """Start transitioning from current opacity to the target opacity."""
        self.transitioning = True
        self.transition_time = 0
        self.target_opacity = target_opacity

    def update_transition(self):
        """Smoothly update the opacity during the transition phase."""
        if self.transition_time < self.transition_duration:
            # Calculate the new opacity using linear interpolation
            t = self.transition_time / self.transition_duration
            self.night_overlay_opacity = int(self.lerp(self.night_overlay_opacity, self.target_opacity, t))
            self.transition_time += 1
        else:
            # End the transition when the time is up
            self.night_overlay_opacity = self.target_opacity
            self.transitioning = False

    def lerp(self, start, end, t):
        """Linearly interpolate between start and end values by t (0 to 1)."""
        return start + t * (end - start)

    def update_thunderstorm(self):
        # Chance to trigger lightning flash
        if random.random() < 0.0005:
            self.trigger_lighting()

        # Update flash effect
        if self.flash_duration > 0:
            self.flash_duration -= 1
            self.flash_alpha = max(0, int(self.flash_alpha * 0.98))  # Fade out

    def trigger_lighting(self, duration=80):
        self.flash_duration = duration
        self.flash_alpha = 150  # Maximum opacity at the start

    def change_weather(self, weather_type):
        self.current_weather = weather_type
        if weather_type == 'clear':
            self.raindrops = None  # No rain
        elif weather_type in ['rain', 'thunderstorm']:
            if weather_type == 'rain':
                self.raindrops = self.rain
            elif weather_type == 'thunderstorm':
                self.raindrops = self.heavy_rain
            elif weather_type == 'snow':
                self.snow = self.snow

    def get_time_of_day(self):
        return 'Day' if self.is_day else 'Night'

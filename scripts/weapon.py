import pygame
import random

class Weapon():
    def __init__ (self, game, weapon_type, damage, cooldown, stamina_cost):
        self.game = game
        self.weapon_type = weapon_type
        self.damage = damage
        self.cooldown = cooldown
        self.stamina_cost = stamina_cost
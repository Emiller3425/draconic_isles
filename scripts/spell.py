import pygame
import random

class Spell():
    def __init__ (self, game, spell_type, damage, mana_cost, velocity, restoration):
        self.game = game
        self.spell_type = spell_type
        self.damage = damage
        self.mana_cost = mana_cost
        self.velocity = velocity
        self.restoration = restoration
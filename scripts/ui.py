import pygame
import json

class UI:
    def __init__(self, game, player, equipped_player_weapon, equipped_player_spell,
                 base_position=(10, 0), base_size=(100, 50), 
                 player_attribute_bar_positions=None, player_attribute_bar_sizes=None):
        self.game = game
        self.player = player
        self.enemies = self.game.enemies

        # Load the custom UI elements
        self.player_attribute_bar_image = game.assets['player_attribute_bar']
        self.minor_enemy_health_bar_image = game.assets['minor_enemy_health_bar']
        self.equipped_weapon_card = game.assets['equipped_weapon_card']
        self.equipped_spell_card = game.assets['equipped_spell_card']
        self.soul_counter_card = game.assets['soul_counter_card']
        self.equipped_player_melee = equipped_player_weapon
        self.equipped_player_spell = equipped_player_spell
        self.grey_digits = game.assets['grey_digits']
        self.red_digits = game.assets['red_digits']
        self.blue_digits = game.assets['blue_digits']
        self.green_digits = game.assets['green_digits']
        self.grey_letters = game.assets['grey_letters']
        self.upgrade_arrow = game.assets['upgrade_arrow']
        self.upgrade_arrow_hover = game.assets['upgrade_arrow_hover']
        self.downgrade_arrow = game.assets['downgrade_arrow']
        self.downgrade_arrow_hover = game.assets['downgrade_arrow_hover']


        # Define the colors for each attribute bar
        self.player_attribute_bar_colors = {
            'health': (139, 0, 0),    # Dark Red for health
            'stamina': (0, 100, 0),   # Dark Green for stamina
            'mana': (0, 0, 139)       # Dark Blue for mana
        }

        self.minor_enemy_health_bar_color = (190, 50, 50)  # Dark Red for enemy health

        # Set the base position and size of the attribute bar background
        self.base_position = base_position
        self.base_width, self.base_height = base_size

        # Set positions for each attribute bar, defaulting to values if not specified
        self.player_attribute_bar_positions = player_attribute_bar_positions or {
            'health': (self.base_position[0] + 23, self.base_position[1] + 8),
            'stamina': (self.base_position[0] + 23, self.base_position[1] + 16),
            'mana': (self.base_position[0] + 23, self.base_position[1] + 20)
        }

        # Set sizes for each attribute bar, defaulting to values if not specified
        self.player_attribute_bar_sizes = player_attribute_bar_sizes or {
            'health': (71, 7),    # Default width and height for health bar
            'stamina': (69, 3),   # Default width and height for stamina bar
            'mana': (44, 3)       # Default width and height for mana bar
        }

    def render(self, surf, render_scroll):
        # Render the base UI element (attribute bar background)
        surf.blit(self.player_attribute_bar_image, (self.base_position[0], self.base_position[1]))

        # Render each attribute bar on top of the base UI element
        self.render_bar(surf, 'health', self.player.health, self.player.max_health)
        self.render_bar(surf, 'stamina', self.player.stamina, self.player.max_stamina)
        self.render_bar(surf, 'mana', self.player.mana, self.player.max_mana)

        # Render health bars for enemies
        for enemy in self.enemies:
            if enemy.health < enemy.max_health:
                self.render_enemy_health_bar(surf, enemy, render_scroll)
        
        # Render equipped cards in the bottom right corner
        self.render_equipped_cards(surf)

        # Render Soul Counter
        self.render_souls(surf, self.player)

    def render_bar(self, surf, attribute, current, maximum):
        # Calculate the percentage to display
        percentage = max(0, current / maximum)  # Ensure percentage is never negative

        # Get the bar position and size
        x, y = self.player_attribute_bar_positions[attribute]
        width, height = self.player_attribute_bar_sizes[attribute]

        # Draw the filled portion of the bar based on the current value
        filled_width = max(0, int(width * percentage))

        if filled_width > 0:

            # Create a filled bar surface of the appropriate color
            filled_bar = pygame.Surface((filled_width, height), pygame.SRCALPHA)
            filled_bar.fill(self.player_attribute_bar_colors[attribute])

            # Blit the filled portion on top of the background
            surf.blit(filled_bar, (x, y))

    def render_enemy_health_bar(self, surf, enemy, render_scroll):
        # Calculate the percentage to display
        percentage = max(0, enemy.health / enemy.max_health)  # Ensure percentage is never negative

        # Define the size of the health bar within the 16x16 frame
        frame_width = 16  # Full frame size
        bar_width, bar_height = 12, 3  # Bar inside the frame (4 pixels high, centered)

        # Position the health bar frame slightly above the enemy
        frame_x = int(enemy.pos[0] - render_scroll[0] + enemy.damage_hitbox[0] // 2 - frame_width // 2)
        frame_y = int(enemy.pos[1] - render_scroll[1] - 20)  # Adjust as needed for desired height above the enemy

        # Draw the health bar background (frame)
        surf.blit(self.minor_enemy_health_bar_image, (frame_x, frame_y))

        # Calculate the position of the filled portion within the frame
        bar_x = int(frame_x + 2)  # 2 pixels padding on each side of the frame
        bar_y = int(frame_y + 6)  # 6 pixels down to center vertically in the 16x16 frame

        # Draw the filled portion of the bar based on the current value
        filled_width = max(0, int(bar_width * percentage))  # Ensure filled_width is at least 0

        # Only draw the filled bar if there's a valid width to display
        if filled_width > 0:
            # Create a filled bar surface of the appropriate color
            filled_bar = pygame.Surface((filled_width, bar_height), pygame.SRCALPHA)
            filled_bar.fill(self.minor_enemy_health_bar_color)

            # Blit the filled portion on top of the background frame
            surf.blit(filled_bar, (bar_x, bar_y))

            # Draw extra pixel at each end of the filled bar
            surf.set_at((bar_x - 1, bar_y + 1), self.minor_enemy_health_bar_color)
            if filled_width == bar_width:
                right_x = int(bar_x + filled_width)
                surf.set_at((right_x, bar_y + 1), self.minor_enemy_health_bar_color)

    def render_equipped_cards(self, surf):
        # Get the screen size to position the cards at the bottom left corner
        _, screen_height = surf.get_size()

        # Determine the positions for the melee and spell cards
        melee_card_position = (5, screen_height - self.equipped_weapon_card.get_height() - 5)
        spell_card_position = (melee_card_position[0] + self.equipped_weapon_card.get_width() + 2, melee_card_position[1])

        # Render the equipped melee card background
        surf.blit(self.equipped_weapon_card, melee_card_position)

        # Render the equipped melee weapon on top of the melee card
        if self.equipped_player_melee:
            melee_image = self.game.assets.get(self.equipped_player_melee)
            if melee_image:
                # Center the melee weapon image on the melee card
                melee_image_position = (
                    melee_card_position[0] + (self.equipped_weapon_card.get_width() - melee_image.get_width()) // 2,
                    melee_card_position[1] + (self.equipped_weapon_card.get_height() - melee_image.get_height()) // 2
                )
                surf.blit(melee_image, melee_image_position)

        # Render the equipped spell card background
        surf.blit(self.equipped_spell_card, spell_card_position)

        # Render the equipped spell on top of the spell card
        if self.equipped_player_spell:
            spell_image = self.game.assets.get(self.equipped_player_spell)
            if spell_image:
                # Center the spell image on the spell card
                spell_image_position = (
                    spell_card_position[0] + (self.equipped_spell_card.get_width() - spell_image.get_width()) // 2,
                    spell_card_position[1] + (self.equipped_spell_card.get_height() - spell_image.get_height()) // 2
                )
                surf.blit(spell_image, spell_image_position)


    def render_boss_health_bar(self, surf, boss):
        # TODO Implement boss health bar rendering when we get here hopefully by thanksgiving 
        pass

    def render_souls(self, surf, player):
        # TODO Implement loop to render the increase so you can see it tick up on enemy kill instaed of instantly changing

        # Shift for each digit rendering
        left_shift = 0
        
        # Max number that can be displayed on the soul counter card
        if player.souls > 9999999999:
            display_souls = "9999999999"
        else:
            display_souls = str(player.souls)

        # Get screen size for rendering
        screen_width, screen_height = surf.get_size()

        # Get position to render soul_counter_card
        soul_counter_card_postition = (screen_width - self.soul_counter_card.get_width() - 5, screen_height - self.soul_counter_card.get_height() - 5)

        # Render the empty soul_counter_card
        surf.blit(self.soul_counter_card, soul_counter_card_postition)

        # Empty string to hold the revered string of souls
        reversed_display_souls = ""

        # Reverse the string for rendering because we render left --> right in the soul_counter_card
        for i in range(0, len(display_souls)):
            reversed_display_souls += display_souls[len(display_souls)-i-1]

        # Loop through and print digits
        for i in reversed_display_souls:
            surf.blit(self.grey_digits[int(i)], (soul_counter_card_postition[0] + 40 - left_shift, soul_counter_card_postition[1] + 6))
            left_shift += 4



    # TODO Use a single function for all this rendering to fix readabillity
    def render_next_level(self, surf, level):
        # Shift for each digit rendering
        left_shift = 0
        
        # Max number that can be displayed on the soul counter card
        display_souls = str(level* 100)


        # Empty string to hold the revered string of souls
        reversed_display_souls = ""

        # Reverse the string for rendering because we render left --> right in the soul_counter_card
        for i in range(0, len(display_souls)):
            reversed_display_souls += display_souls[len(display_souls)-i-1]
            
        # Loop through and print digits
        for i in reversed_display_souls:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 713, surf.get_height() - 587)), (485 - left_shift, 526))
            left_shift += 9

    def render_health(self, surf, player):
        left_shift = 0

        if player.max_health > 9999999999:
            display_health = "9999999999"
        else:
            display_health = str(player.max_health)
        
        # Get screen size for rendering
        screen_width, screen_height = surf.get_size()

        reversed_display_health = ""

        for i in range(0, len(display_health)):
            reversed_display_health += display_health[len(display_health)-i-1]

                # Loop through and print digits
        for i in reversed_display_health:
            pygame.transform.scale(self.red_digits[int(i)], surf.get_size())
            # TODO draw out th rest of the upgrade screen and how we want it.
            # How we will transform sizes of digits and shit
            surf.blit(pygame.transform.scale(self.red_digits[int(i)], (surf.get_width() - 710, surf.get_height() - 585)), (420 - left_shift, 161))
            left_shift += 12

    def render_stamina(self, surf, player):
        left_shift = 0

        if player.max_stamina > 9999999999:
            display_stamina = "9999999999"
        else:
            display_stamina = str(player.max_stamina)
        
        # Get screen size for rendering
        screen_width, screen_height = surf.get_size()

        reversed_display_stamina = ""

        for i in range(0, len(display_stamina)):
            reversed_display_stamina += display_stamina[len(display_stamina)-i-1]

                # Loop through and print digits
        for i in reversed_display_stamina:
            surf.blit(pygame.transform.scale(self.green_digits[int(i)], (surf.get_width() - 710, surf.get_height() - 585)), (420 - left_shift, 281))
            left_shift += 12

    def render_mana(self, surf, player):
        left_shift = 0

        if player.max_mana > 9999999999:
            display_mana = "9999999999"
        else:
            display_mana = str(player.max_mana)
        
        # Get screen size for rendering
        screen_width, screen_height = surf.get_size()

        reversed_display_mana = ""

        for i in range(0, len(display_mana)):
            reversed_display_mana += display_mana[len(display_mana)-i-1]

        # Loop through and print digits
        for i in reversed_display_mana:
            surf.blit(pygame.transform.scale(self.blue_digits[int(i)], (surf.get_width() - 710, surf.get_height() - 585)), (420 - left_shift, 401))
            left_shift += 12

    def render_weapon_name_stats(self, surf, player, weapon):
        left_shift = 0

        temp_reversed_weapon_damage = str(weapon.damage)
        reversed_weapon_damage = ""
        for i in range(0, len(temp_reversed_weapon_damage)):
            reversed_weapon_damage += temp_reversed_weapon_damage[len(temp_reversed_weapon_damage)-i-1]
        
        temp_reversed_weapon_cooldown = str(weapon.cooldown)
        reversed_weapon_cooldown = ""
        for i in range(0, len(temp_reversed_weapon_cooldown)):
            reversed_weapon_cooldown += temp_reversed_weapon_cooldown[len(temp_reversed_weapon_cooldown)-i-1]

        temp_reversed_weapon_stamina_cost = str(weapon.stamina_cost)
        reversed_weapon_stamina_cost = ""
        for i in range(0, len(temp_reversed_weapon_stamina_cost)):
            reversed_weapon_stamina_cost += temp_reversed_weapon_stamina_cost[len(temp_reversed_weapon_stamina_cost)-i-1]

        reversed_weapon_name = ""

        for i in range(0, len(weapon.weapon_type)):
            reversed_weapon_name += weapon.weapon_type[len(weapon.weapon_type)-i-1]

        for i in reversed_weapon_name:
            if i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 714, surf.get_height() - 591)), (565 - left_shift, 200))
            left_shift += 7
        
        left_shift = 0

        for i in ':egamad':
            if i == ':':
                index = 27
            elif i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 716, surf.get_height() - 591)), (515 - left_shift, 218))
            left_shift += 5
        
        left_shift = 0

        for i in reversed_weapon_damage:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 716, surf.get_height() - 591)), (585 - left_shift, 218))
            left_shift += 5

        left_shift = 0

        for i in ':nwodlooc':
            if i == ':':
                index = 27
            elif i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 716, surf.get_height() - 591)), (525 - left_shift, 230))
            left_shift += 5
        left_shift = 0

        for i in reversed_weapon_cooldown:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 716, surf.get_height() - 591)), (585 - left_shift, 230))
            left_shift += 5

        left_shift = 0

        for i in ':tsoc_animats':
            if i == ':':
                index = 27
            elif i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 716, surf.get_height() - 591)), (545 - left_shift, 242))
            left_shift += 5

        left_shift = 0

        for i in reversed_weapon_stamina_cost:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 716, surf.get_height() - 591)), (585 - left_shift, 242))
            left_shift += 5


    def render_spell_name_stats(self, surf, player, spell):
        left_shift = 0

        temp_reversed_spell_damage = str(spell.damage)
        reversed_spell_damage = ""
        for i in range(0, len(temp_reversed_spell_damage)):
            reversed_spell_damage += temp_reversed_spell_damage[len(temp_reversed_spell_damage)-i-1]
        
        temp_reversed_spell_mana_cost = str(spell.mana_cost)
        reversed_spell_mana_cost = ""
        for i in range(0, len(temp_reversed_spell_mana_cost)):
            reversed_spell_mana_cost+= temp_reversed_spell_mana_cost[len(temp_reversed_spell_mana_cost)-i-1]

        temp_reversed_spell_velocity = str(spell.velocity)
        reversed_spel_velocity = ""
        for i in range(0, len(temp_reversed_spell_velocity)):
            reversed_spel_velocity += temp_reversed_spell_velocity[len(temp_reversed_spell_velocity)-i-1]

        reversed_spell_name = ""

        for i in range(0, len(spell.spell_type)):
            reversed_spell_name += spell.spell_type[len(spell.spell_type)-i-1]

        for i in reversed_spell_name:
            if i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 714, surf.get_height() - 591)), (565 - left_shift, 415))
            left_shift += 7
        
        left_shift = 0

        for i in ':egamad':
            if i == ':':
                index = 27
            elif i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 716, surf.get_height() - 591)), (515 - left_shift, 430))
            left_shift += 5
        
        left_shift = 0

        for i in reversed_spell_damage:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 716, surf.get_height() - 591)), (585 - left_shift, 430))
            left_shift += 5
        
        left_shift = 0

        for i in ':tsoc_anam':
            if i == ':':
                index = 27
            elif i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 716, surf.get_height() - 591)), (530 - left_shift, 442))
            left_shift += 5

        left_shift = 0

        for i in reversed_spell_mana_cost:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 716, surf.get_height() - 591)), (585 - left_shift, 442))
            left_shift += 5

        left_shift = 0

        for i in ':yticolev':
            if i == ':':
                index = 27
            elif i == '_':
                index = 26
            else:
                index = ord(i) - 97
            surf.blit(pygame.transform.scale(self.grey_letters[int(index)], (surf.get_width() - 716, surf.get_height() - 591)), (525 - left_shift, 454))
            left_shift += 5
        
        left_shift = 0

        for i in reversed_spel_velocity:
            surf.blit(pygame.transform.scale(self.grey_digits[int(i)], (surf.get_width() - 716, surf.get_height() - 591)), (585 - left_shift, 454))
            left_shift += 5


        # Render restoration if I end up doing anything with that
        
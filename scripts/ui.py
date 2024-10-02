import pygame

class UI:
    def __init__(self, game, player, equipped_player_melee, equipped_player_spell,
                 base_position=(10, 0), base_size=(100, 50), 
                 player_attribute_bar_positions=None, player_attribute_bar_sizes=None):
        self.game = game
        self.player = player
        self.enemies = self.game.enemies

        # Load the custom UI elements
        self.player_attribute_bar_image = game.assets['player_attribute_bar']
        self.minor_enemy_health_bar_image = game.assets['minor_enemy_health_bar']
        self.equipped_melee_card = game.assets['equipped_melee_card']
        self.equipped_spell_card = game.assets['equipped_spell_card']
        self.equipped_player_melee = equipped_player_melee
        self.equipped_player_spell = equipped_player_spell


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
        melee_card_position = (5, screen_height - self.equipped_melee_card.get_height() - 5)
        spell_card_position = (melee_card_position[0] + self.equipped_melee_card.get_width() + 2, melee_card_position[1])

        # Render the equipped melee card background
        surf.blit(self.equipped_melee_card, melee_card_position)

        # Render the equipped melee weapon on top of the melee card
        if self.equipped_player_melee:
            melee_image = self.game.assets.get(self.equipped_player_melee)
            if melee_image:
                # Center the melee weapon image on the melee card
                melee_image_position = (
                    melee_card_position[0] + (self.equipped_melee_card.get_width() - melee_image.get_width()) // 2,
                    melee_card_position[1] + (self.equipped_melee_card.get_height() - melee_image.get_height()) // 2
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
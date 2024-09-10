import pygame

class UI:
    def __init__(self, game, player, 
                 base_position=(10, 0), base_size=(100, 50), 
                 bar_positions=None, bar_sizes=None):
        self.game = game
        self.player = player

        # Load the custom UI element (base image for the attribute bar background)
        self.bar_image = game.assets['attribute_bar']

        # Define the colors for each attribute bar
        self.bar_colors = {
        'health': (139, 0, 0),    # Dark Red for health
        'stamina': (0, 100, 0),   # Dark Green for stamina
        'mana': (0, 0, 139)       # Dark Blue for mana
        }

        # Set the base position and size of the attribute bar background
        self.base_position = base_position
        self.base_width, self.base_height = base_size

        # Set positions for each attribute bar, defaulting to values if not specified
        self.bar_positions = bar_positions or {
            'health': (self.base_position[0] + 23, self.base_position[1] + 8),
            'stamina': (self.base_position[0] + 23, self.base_position[1] + 16),
            'mana': (self.base_position[0] + 23, self.base_position[1] + 20)
        }

        # Set sizes for each attribute bar, defaulting to values if not specified
        self.bar_sizes = bar_sizes or {
            'health': (71, 7),    # Default width and height for health bar
            'stamina': (69, 3),   # Default width and height for stamina bar
            'mana': (44, 3)       # Default width and height for mana bar
        }

    def render(self, surf):
        # Render the base UI element (attribute bar background)
        surf.blit(self.bar_image, (self.base_position[0], self.base_position[1]))

        # Render each attribute bar on top of the base UI element
        self.render_bar(surf, 'health', self.player.health, self.player.max_health)
        self.render_bar(surf, 'stamina', self.player.stamina, self.player.max_stamina)
        self.render_bar(surf, 'mana', self.player.mana, self.player.max_mana)

    def render_bar(self, surf, attribute, current, maximum):
        # Calculate the percentage to display
        percentage = current / maximum

        # Get the bar position and size
        x, y = self.bar_positions[attribute]
        width, height = self.bar_sizes[attribute]

        # Draw the filled portion of the bar based on the current value
        filled_width = int(width * percentage)

        # Create a filled bar surface of the appropriate color
        filled_bar = pygame.Surface((filled_width, height), pygame.SRCALPHA)
        filled_bar.fill(self.bar_colors[attribute])

        # Blit the filled portion on top of the background
        surf.blit(filled_bar, (x, y))

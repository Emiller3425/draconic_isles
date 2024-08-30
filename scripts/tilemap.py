import pygame
import pytmx

NEIGHBORS_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILE_TYPES = {'walls'}
# INTRERACTABLE_TILE_TYPES = {'ladder'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.tile_size = tile_size
        self.game = game
        self.tilemap = {}
        self.offgrid_tiles = []
        self.player_position = (0, 0)
        self.enemy_positions = []
        self.boss_positions = []
        self.trees = []
        self.boss_counter = 0

    def load(self):
        # Load the map tilemap
        self.tmx_data = pytmx.load_pygame('./levels/test_level/test_level.tmx')

        # Iterate through the layers and create the tilemap
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            for x, y, surf in layer.tiles():
                key = str(x) + ';' + str(y)
                if key not in self.tilemap:
                    self.tilemap[key] = []
                if layer.name == 'walls':
                    self.tilemap[key].append({'type': 'walls', 'variant': 0, 'pos': (x, y), 'layer': layer_index})
                if layer.name == 'player':
                    self.player_position = (x, y)

    def get_all_tiles(self):
        """
        Get all tiles and their locations from the tilemap.

        :return: List of dictionaries containing tile information, including location and type.
        """
        all_tiles = []
        for key, tiles in self.tilemap.items():
            for tile in tiles:
                # Each tile entry contains its location, type, and other attributes
                tile_info = {
                    'type': tile['type'],
                    'variant': tile['variant'],
                    'pos': tile['pos'],
                    'layer': tile['layer']
                }
                all_tiles.append(tile_info)
        return all_tiles
                        

    def tiles_arounds(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBORS_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.extend(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos, entity_size):
        """
        Find all physics-related rectangles around the given position
        considering the size of the entity.

        :param pos: Position of the entity (x, y).
        :param entity_size: Size of the entity (width, height).
        :return: List of pygame.Rect representing the physics collision boxes.
        """
        rects = []
        # Calculate the number of tiles the entity covers
        start_tile_x = int(pos[0] // self.tile_size)
        end_tile_x = int((pos[0] + entity_size[0]) // self.tile_size) + 1
        start_tile_y = int(pos[1] // self.tile_size)
        end_tile_y = int((pos[1] + entity_size[1]) // self.tile_size) + 1

        for x in range(start_tile_x, end_tile_x):
            for y in range(start_tile_y, end_tile_y):
                check_loc = f"{x};{y}"
                if check_loc in self.tilemap:
                    for tile in self.tilemap[check_loc]:
                        if tile['type'] in PHYSICS_TILE_TYPES:
                            rect = pygame.Rect(
                                tile['pos'][0] * self.tile_size,
                                tile['pos'][1] * self.tile_size,
                                tile.get('width', self.tile_size),
                                tile.get('height', self.tile_size)
                            )
                            rects.append(rect)
        return rects
    

    # def render(self, surf, offset=(0, 0)):
    #         """
    #         Render the tilemap to the given surface.

    #         :param surf: The surface to render the tiles on.
    #         :param offset: The offset to apply to the rendering position.
    #         """
    #         # Render off-grid tiles
    #         for tile in self.offgrid_tiles:
    #             self.render_tile(surf, tile, offset)

    #         # Render tiles on the grid within the visible area
    #         for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
    #             for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
    #                 loc = str(x) + ';' + str(y)
    #                 if loc in self.tilemap:
    #                     for tile in sorted(self.tilemap[loc], key=lambda t: t['layer']):
    #                         self.render_tile(surf, tile, offset)

    def render_tile(self, surf, tile, offset):
        """
        Render a single tile on the given surface.

        :param surf: The surface to render the tile on.
        :param tile: The tile data dictionary.
        :param offset: The offset to apply to the tile's position.
        """
        tile_type = tile['type']
        variant = tile['variant']
        pos = tile['pos']
        x_pos = pos[0] * self.tile_size - offset[0]
        y_pos = pos[1] * self.tile_size - offset[1]

        # Only render tiles within the screen bounds
        if (-16 <= x_pos < surf.get_width() + 16) and (-16 <= y_pos < surf.get_height() + 16):
            surf.blit(
                self.game.assets[tile_type][variant], 
                (x_pos, y_pos)
            )
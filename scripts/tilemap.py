import pygame
import pytmx

NEIGHBORS_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILE_TYPES = {
    'walls', 
    'bush', 
    'light', 
    'tree'
    }

PHYSICS_TILE_HITBOXES = {
    'walls': {
        0: (16, 16),
        1: (16, 16),
        2: (16, 16),
    },
    'bush': {
        0: (16, 16),
    },
    'light': {
        0: (12, 14),
    },
    'tree': {
        0: (16, 16),
        1: (16, 16),
        2: (16, 16),
        3: (16, 16),
    }
}

NON_ORDER_TILES = {
    'ground',
    }

# INTRERACTABLE_TILE_TYPES = {'ladder'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.tile_size = tile_size
        self.game = game
        self.tilemap = {}
        self.tilemap_layer_data_values = {}
        self.offgrid_tiles = []
        self.player_position = (0, 0)
        self.enemy_positions = []
        self.boss_positions = []
        self.trees = []
        self.boss_counter = 0

    def load(self):
        # Load the map tilemap
        self.tmx_data = pytmx.load_pygame('./levels/test_level_2/test_level_2.tmx')

        # TODO, find all the numbers in each layer so you don't have to manually chnage the numbers everytime you add new assets/layers,
        # because this is going to be really fucking annoying
        for layer in enumerate(self.tmx_data.visible_layers):
            pass
            

        # Iterate through the layers and create the tilemap
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            for x, y, surf in layer.tiles():
                key = str(x) + ';' + str(y)
                if key not in self.tilemap:
                    self.tilemap[key] = []
                if layer.name == 'ground':
                    if layer.data[y][x] == 1:
                        self.tilemap[key].append({'type': 'ground', 'variant': 0, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 2:
                        self.tilemap[key].append({'type': 'ground', 'variant': 1, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 3:
                        self.tilemap[key].append({'type': 'ground', 'variant': 2, 'pos': (x, y), 'layer': layer_index})
                if layer.name == 'walls':
                    if layer.data[y][x] == 4:
                        self.tilemap[key].append({'type': 'walls', 'variant': 0, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 5:
                        self.tilemap[key].append({'type': 'walls', 'variant': 1, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 6:
                        self.tilemap[key].append({'type': 'walls', 'variant': 2, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 7:
                        self.tilemap[key].append({'type': 'walls', 'variant': 3, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 8:
                        self.tilemap[key].append({'type': 'walls', 'variant': 4, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 9:
                        self.tilemap[key].append({'type': 'walls', 'variant': 5, 'pos': (x, y), 'layer': layer_index})
                # TODO Rename this layer to lights in Tiled, needs to be more general for all light sources, there will be more claseses for each light in the future
                if layer.name == 'lantern':
                    self.tilemap[key].append({'type': 'light', 'variant': 0, 'pos': (x, y), 'layer': layer_index})
                if layer.name == 'bush':
                    self.tilemap[key].append({'type': 'bush', 'variant': 0, 'pos': (x, y), 'layer': layer_index})
                if layer.name == 'tree':
                    if layer.data[y][x] == 12:
                        self.tilemap[key].append({'type': 'tree', 'variant': 0, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 13:
                        self.tilemap[key].append({'type': 'tree', 'variant': 1, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 14:
                        self.tilemap[key].append({'type': 'tree', 'variant': 2, 'pos': (x, y), 'layer': layer_index})
                    if layer.data[y][x] == 15:
                        self.tilemap[key].append({'type': 'tree', 'variant': 3, 'pos': (x, y), 'layer': layer_index})
                if layer.name == 'player':
                    self.player_position = (x, y)
                # TODO Change to layer to skeleton here and in tiled as more enemies are added
                if layer.name == 'enemy':
                    self.enemy_positions.append((x, y))
                # TODO: Add enemy locations as more are added and boss positions
    
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in list(self.tilemap.keys()):
            for tile in self.tilemap[loc]:
                if (tile['type'], tile['variant']) in id_pairs:
                    match = tile.copy()
                    match['pos'] = list(match['pos'])
                    match['pos'][0] *= self.tile_size
                    match['pos'][1] *= self.tile_size
                    matches.append(match)
                    if not keep:
                        self.tilemap[loc].remove(tile)
                        if not self.tilemap[loc]:  # Remove the key if the list is empty
                            del self.tilemap[loc]

        return matches

    def get_all_ordered_tiles(self):
        """
        Get all tiles and their locations from the tilemap.

        :return: List of dictionaries containing tile information, including location and type.
        """
        all_tiles = []
        for key, tiles in self.tilemap.items():
            for tile in tiles:
                if tile['type'] not in NON_ORDER_TILES:
                    # Each tile entry contains its location, type, and other attributes
                    tile_info = {
                        'type': tile['type'],
                        'variant': tile['variant'],
                        'pos': tile['pos'],
                        'layer': tile['layer']
                    }
                    all_tiles.append(tile_info)
        return all_tiles    

    def get_all_non_ordered_tiles(self):
        """
        Get all tiles and their locations from the tilemap.

        :return: List of dictionaries containing tile information, including location and type.
        """
        all_tiles = []
        for key, tiles in self.tilemap.items():
            for tile in tiles:
                if tile['type'] in NON_ORDER_TILES:
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
                       # Exclude tiles based on their type and variant
                        if tile['type'] in PHYSICS_TILE_TYPES:
                            width, height = PHYSICS_TILE_HITBOXES.get(tile['type'], {}).get(tile['variant'], (self.tile_size, self.tile_size))
                            rect = pygame.Rect(
                                tile['pos'][0] * self.tile_size + ((self.tile_size - width) / 2),
                                tile['pos'][1] * self.tile_size + ((self.tile_size - height) / 2),
                                width,
                                height
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

        # Tiles and variants to render over the plyer
        deferred_tiles = None # tile_type == 'tree' and variant in [0, 1]

        # Render all non-tree-top tiles
        if not deferred_tiles:
            # Only render tiles within the screen bounds
            if (-16 <= x_pos < surf.get_width() + 16) and (-16 <= y_pos < surf.get_height() + 16):
                surf.blit(
                    self.game.assets[tile_type][variant], 
                    (x_pos, y_pos)
                )
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
        0: (0, 0),
        1: (0, 0),
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
        self.object_layers = {
            'player' : {'positions': [], 'variants': []},
            'skeleton' : {'positions': [], 'variants': []},
            'bonfire' : {'positions': [], 'variants': []},
        }
        self.animated_layers = {
            # TODO try bush first after bottom left most occurances is dones
        }
        self.offgrid_tiles = []
        self.player_position = (0, 0)
        self.enemy_positions = []
        self.boss_positions = []
        self.trees = []

    def load(self):
        # Load the map tilemap
        self.tmx_data = pytmx.load_pygame('./levels/test_level_2/test_level_2.tmx')

        # create dictionary with key = layer names and values an array on integers in the data
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            self.tilemap_layer_data_values.update({layer.name:[]})

        # Add integer values of each layer into corresponding layer       
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            for x, y , surf in layer.tiles():
                if layer.data[y][x] not in self.tilemap_layer_data_values[layer.name]:
                    self.tilemap_layer_data_values[layer.name].append(layer.data[y][x])
        
        # Match value within the layer to the variant that is the corresponding index of the layer
        for layer_index, layer in enumerate(self.tmx_data.visible_layers):
            for x, y, surf in layer.tiles():
                key = str(x) + ';' + str(y)
                if key not in self.tilemap:
                    self.tilemap[key] = []
                if layer.data[y][x] != 0:
                    if layer.data[y][x] in self.tilemap_layer_data_values[layer.name]:
                        if layer.name not in self.object_layers and layer.name not in self.animated_layers:
                            self.tilemap[key].append({'type': layer.name, 'variant': self.tilemap_layer_data_values[layer.name].index(layer.data[y][x]), 'pos': (x, y), 'layer': layer_index})
                        for k in self.object_layers:
                            if layer.name == k:
                                self.object_layers[k]['positions'].append((x,y))
                                self.object_layers[k]['variants'].append(self.tilemap_layer_data_values[layer.name].index(layer.data[y][x]))
                        for k in self.animated_layers:
                            if layer.name == k:
                                self.animated_layers[k]['positions'].append((x,y))

        variants = self.get_bottom_left_most_variants()

        # TODO Get all occurances of bottom left-most variant
        
    def get_bottom_left_most_variants(self):
        bottom_left_positions = {}
        bottom_left_variants = {}
        for k in self.object_layers:
            bottom_left_pos = (0, 0)
            for v in self.object_layers[k]:
                if v != 'variants':
                    for i in self.object_layers[k][v]:
                        if bottom_left_pos[1] < i[1]:
                            bottom_left_pos = i
                        elif bottom_left_pos[0] > i[0]:
                            bottom_left_pos = i
                    bottom_left_positions[k] = []
                    bottom_left_positions[k].append(bottom_left_pos)
                    bottom_left_index = self.object_layers[k][v].index(bottom_left_positions[k][0])
                    bottom_left_variants[k] = []
                    y = self.object_layers[k]['variants'][bottom_left_index]
                    bottom_left_variants[k] = []
                    bottom_left_variants[k].append(y)
                                  
        return bottom_left_variants

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

    def get_animated_tiles(self):
        """
        Find and return all animated tiles such as bonfires.
        """
        all_tiles = []
        for key, tiles in self.tilemap.items():
            for tile in tiles:
                if tile['type'] in self.animated_tiles:
                    tile_info = {
                        'type': tile['type'],
                        'variant': tile['variant'],
                        'pos': tile['pos'],
                        'layer': tile['layer'],
                        'animation': self.game.assets[tile['type'] + '/animation'].copy()  # Add animation for bonfire
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

        # Render all non-deferred tiles
        if not deferred_tiles and tile_type not in self.animated_layers:
            # Only render tiles within the screen bounds
            if (-16 <= x_pos < surf.get_width() + 16) and (-16 <= y_pos < surf.get_height() + 16):
                surf.blit(
                    self.game.assets[tile_type][variant], 
                    (x_pos, y_pos)
                )

    

            


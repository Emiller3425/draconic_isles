import pygame
import random
from scripts.light import Light

class MultiAnimated:
    def __init__(self, game, tile_type, positions, frame=0):
        self.game = game
        self.tile_type = tile_type
        self.positions = []
        for position in positions:
            self.positions.append((position[0] * self.game.tilemap.tile_size, position[1] * self.game.tilemap.tile_size))
            # if tile_type == 'lava':
            #     self.game.lights.append(Light(self.game, (position[0] * self.game.tilemap.tile_size, position[1] * self.game.tilemap.tile_size), 25, [70, 20, 0]))
        self.flip = False
        self.anim_offset = (0, 0)

        # Copy the animation from your assets
        self.animation = self.game.assets[self.tile_type + '/animation'].copy()

        # Set starting frame (if you want a random start for lava, do `frame=random.randint(...)`)
        self.frame = frame
        self.animation.frame = self.frame * self.animation.img_duration

    def update(self):
        """
        Update the animation frames, but only if at least one tile is near the player 
        (optional optimization). Otherwise, you can just do self.animation.update()
        unconditionally to animate all the time.
        """

        # OPTIONAL: Check if ANY tile is near the player. If so, update the animation.
        # This prevents us from looping over thousands of tiles each frame.
        player_tile_x = self.game.player.pos[0] // self.game.tilemap.tile_size
        player_tile_y = self.game.player.pos[1] // self.game.tilemap.tile_size

        # We'll do a quick bounding check for each tile; 
        # if ANY tile is in range, update the animation
        should_animate = False
        for (tx, ty) in self.positions:
            if (tx // self.game.tilemap.tile_size > player_tile_x - 14 and
                tx // self.game.tilemap.tile_size < player_tile_x + 14 and
                ty // self.game.tilemap.tile_size > player_tile_y - 12 and
                ty // self.game.tilemap.tile_size < player_tile_y + 12):
                should_animate = True
                break

        if should_animate:
            self.animation.update()

    def render(self, surf, offset=(0, 0)):
        """
        Render the current animation frame at each tile position, 
        but ONLY if that tile is near the player.
        """

        current_img = self.animation.img()
        player_tile_x = self.game.player.pos[0] // self.game.tilemap.tile_size
        player_tile_y = self.game.player.pos[1] // self.game.tilemap.tile_size

        for (tx, ty) in self.positions:
            # Same proximity checks as in your Animated.render
            if (tx // self.game.tilemap.tile_size > player_tile_x - 14 and
                tx // self.game.tilemap.tile_size < player_tile_x + 14 and
                ty // self.game.tilemap.tile_size > player_tile_y - 12 and
                ty // self.game.tilemap.tile_size < player_tile_y + 12):


                # Calculate screen position, apply offset
                x_pos = (tx - offset[0] + self.anim_offset[0])
                y_pos = (ty - offset[1] + self.anim_offset[1])

                surf.blit(
                    pygame.transform.flip(current_img, self.flip, False),
                    (x_pos, y_pos)
                )
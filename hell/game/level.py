import random

import pymunk

from . import GameObject, Pawn, WIDTH, HEIGHT

ENEMY_WEIGHTS = {
    Pawn: 1
}


def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


class Level(GameObject):
    def __init__(self, *, batch, player):
        super().__init__()
        self.batch = batch
        self.player = player

        self.enemy_timer = 0

        self.enemy_types_list = list(ENEMY_WEIGHTS.keys())
        self.enemy_weights_list = list(ENEMY_WEIGHTS.values())

    def tick(self, dt: float):
        self.enemy_timer += dt

        if self.enemy_timer >= 0.3:
            enemy_type = random.choices(self.enemy_types_list, self.enemy_weights_list)[0]

            # If player is in the middle
            middle_bb = pymunk.BB.newForCircle((WIDTH / 2, HEIGHT / 2), 50)
            if middle_bb.contains_vect(self.player.pos):
                # Pick a random place to spawn the enemy
                # Pick left, top, right, bottom side
                side = random.choice([0, 1, 2, 3])
                if side == 0:
                    pos = (100, random.randrange(100, HEIGHT - 100))
                elif side == 1:
                    pos = (random.randrange(100, WIDTH - 100), HEIGHT - 100)
                elif side == 2:
                    pos = (WIDTH - 100, random.randrange(100, HEIGHT - 100))
                else:
                    pos = (random.randrange(100, WIDTH - 100), 100)
            else:
                x, y = self.player.pos
                x = WIDTH / 2 - (x - WIDTH / 2)
                x = clamp(x, 100, WIDTH - 100)
                y = HEIGHT / 2 - (y - HEIGHT / 2)
                y = clamp(y, 100, HEIGHT - 100)
                x_wall_dir = min(x, WIDTH - x)
                y_wall_dir = min(y, HEIGHT - y)
                if x_wall_dir < y_wall_dir:
                    x = 100 if x < WIDTH / 2 else WIDTH - 100
                else:
                    y = 100 if y < HEIGHT / 2 else HEIGHT - 100
                pos = (x, y)

            self.new_objects += [enemy_type(pos=pos, player=self.player, batch=self.batch)]
            self.enemy_timer = 0

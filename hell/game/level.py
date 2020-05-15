import random
from collections import namedtuple

import pymunk

from . import GameObject, Pawn, WIDTH, HEIGHT, Slider, Pellet

EnemyData = namedtuple('EnemyData', 'type, weight, cap')

enemy_data = [
    EnemyData(Pawn, 100, 100),
    EnemyData(Slider, 20, 2),
]


def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


class Level(GameObject):
    def __init__(self, *, batch, player):
        super().__init__()
        self.batch = batch
        self.player = player

        self.enemy_timer = 2

        self.spawned_enemies = {enemy.type: 0 for enemy in enemy_data}

        self.spawn_pellet()

    def tick(self, dt: float):
        self.enemy_timer += dt

        if self.enemy_timer >= 2:
            # Choose a random enemy taking weight and max cap into account
            enemies = [(enemy.type, enemy.weight) for enemy in enemy_data if
                       self.spawned_enemies[enemy.type] < enemy.cap]
            if len(enemies) < 1:
                return
            types, weights = zip(*enemies)
            enemy_type = random.choices(types, weights)[0]
            self.spawned_enemies[enemy_type] += 1
            size_x, size_y = enemy_type.START_SIZE / 2

            # If player is in the middle
            middle_bb = pymunk.BB.newForCircle((WIDTH / 2, HEIGHT / 2), 50)
            if middle_bb.contains_vect(self.player.pos):
                # Pick a random place to spawn the enemy
                # Pick left, top, right, bottom side
                side = random.choice([0, 1, 2, 3])
                if side == 0:
                    pos = (size_x, random.randrange(size_y, HEIGHT - size_y))
                elif side == 1:
                    pos = (random.randrange(size_x, WIDTH - size_x), HEIGHT - size_y)
                elif side == 2:
                    pos = (WIDTH - size_x, random.randrange(size_y, HEIGHT - size_y))
                else:
                    pos = (random.randrange(size_x, WIDTH - size_x), size_y)
            else:
                x, y = self.player.pos
                x = WIDTH / 2 - (x - WIDTH / 2)
                x = clamp(x, size_x, WIDTH - size_x)
                y = HEIGHT / 2 - (y - HEIGHT / 2)
                y = clamp(y, size_y, HEIGHT - size_y)
                x_wall_dir = min(x, WIDTH - x)
                y_wall_dir = min(y, HEIGHT - y)
                if x_wall_dir < y_wall_dir:
                    x = size_x if x < WIDTH / 2 else WIDTH - size_x
                else:
                    y = size_y if y < HEIGHT / 2 else HEIGHT - size_y
                pos = (x, y)

            self.new_objects += [enemy_type(pos=pos, player=self.player, batch=self.batch)]
            self.enemy_timer = 0

    def spawn_pellet(self):
        x = random.randrange(100, WIDTH - 100)
        y = random.randrange(100, HEIGHT - 100)
        self.new_objects += [Pellet(pos=(x, y), batch=self.batch)]

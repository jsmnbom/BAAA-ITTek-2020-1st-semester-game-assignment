import random
from collections import namedtuple

import pymunk

from . import GameObject, EnemyPawn, WIDTH, HEIGHT, EnemySlider, Pellet

# Type to score data about enemies
# Weight is how likely they are to spawn
# Cap is how many can exist at once at the most
EnemyData = namedtuple('EnemyData', 'type, weight, cap')

enemy_data = [
    #EnemyData(EnemyPawn, 100, 100),
    EnemyData(EnemySlider, 20, 2),
]


def clamp(value, lower, upper):
    """Clamps value between lower and upper"""
    return lower if value < lower else upper if value > upper else value


class Level(GameObject):
    """Level that handles spawning of pellets and enemies."""

    def __init__(self, *, batch, player):
        super().__init__()
        self.batch = batch
        self.player = player

        self.enemy_timer = 2

        # Keep track of how many enemies of each type we've spawned
        # so we can keep it under its cap
        self.spawned_enemies = {enemy.type: 0 for enemy in enemy_data}

        # Spawn the first pellet
        # Additional pellets are spawned in the pellet collision callback
        self.spawn_pellet()

    def tick(self, dt: float):
        self.enemy_timer += dt

        # If it's time to spawn an enemy
        if self.enemy_timer >= 2:
            # Choose a random enemy taking weight and max cap into account
            enemies = [(enemy.type, enemy.weight) for enemy in enemy_data if
                       self.spawned_enemies[enemy.type] < enemy.cap]
            # If we have no more enemies to spawn (all have reached their cap) then abort
            if len(enemies) < 1:
                return
            # Get types and weights as two separate lists
            types, weights = zip(*enemies)
            # Choose a type based on the weights
            enemy_type = random.choices(types, weights)[0]
            # We've now spawned another one of this type
            self.spawned_enemies[enemy_type] += 1
            # Get the size of the enemy
            # But divide by 2, cause we only need it to determine how far from wall to spawn the enemy
            size_x, size_y = enemy_type.SIZE / 2

            # If player is in the middle
            middle_bb = pymunk.BB.newForCircle((WIDTH / 2, HEIGHT / 2), 50)
            if middle_bb.contains_vect(self.player.pos):
                # Pick a random place to spawn the enemy
                # Pick left, top, right, bottom side and pick a random position on that wall
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
                # Otherwise, then find a position that is far away from the player
                # The below code is very math heavy but effectively finds a position that is on a inner
                # rectangle as close to the walls as possible (that the enemy can fit), but
                # also as far away from the player as possible
                x, y = self.player.pos
                # Mirror players's x and y over the enter axis point and then clamp
                # it as close to the wall as possible for this enemy
                x = WIDTH / 2 - (x - WIDTH / 2)
                x = clamp(x, size_x, WIDTH - size_x)
                y = HEIGHT / 2 - (y - HEIGHT / 2)
                y = clamp(y, size_y, HEIGHT - size_y)
                # Find distances to walls
                x_wall_dir = abs(min(x, WIDTH - x))
                y_wall_dir = abs(min(y, HEIGHT - y))
                # If the x wall is closer then clamp it close to that one
                if x_wall_dir < y_wall_dir:
                    x = size_x if x < WIDTH / 2 else WIDTH - size_x
                else:
                    y = size_y if y < HEIGHT / 2 else HEIGHT - size_y
                # Then save that position
                pos = (x, y)

            # Spawn an enemy at the found position
            self.new_objects += [enemy_type(pos=pos, player=self.player, batch=self.batch)]
            self.enemy_timer = 0

    def spawn_pellet(self):
        # Find a random place at least 100px away from the walls
        x = random.randrange(100, WIDTH - 100)
        y = random.randrange(100, HEIGHT - 100)
        # And then spawn a pellet there
        self.new_objects += [Pellet(pos=(x, y), batch=self.batch)]

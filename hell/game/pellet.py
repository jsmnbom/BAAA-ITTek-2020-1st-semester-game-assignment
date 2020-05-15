import pymunk

from . import Actor, resources, CollisionType


class Pellet(Actor):
    def __init__(self, *, pos, batch=None, **kwargs):
        size = (8, 8)
        mass = 50
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, size, 0)
        shape.collision_type = CollisionType.Pellet
        super().__init__(body=body, shape=shape, img=resources.pellet_image, batch=batch, pos=pos, **kwargs)

    def on_player_collide(self, game_window):
        # It takes a little bit for the object to die, don't spawn more than one no matter one
        if not self.dead:
            game_window.level.spawn_pellet()
            game_window.ui.score += 1
            self.die()

    @staticmethod
    def init_collision(game_window):
        def pre_solve(arbiter, space, data):
            arbiter.shapes[1].owner.on_player_collide(game_window)
            return False

        collision_handler = game_window.space.add_collision_handler(CollisionType.Player, CollisionType.Pellet)
        collision_handler.pre_solve = pre_solve

        collision_handler = game_window.space.add_collision_handler(CollisionType.Enemy, CollisionType.Pellet)
        collision_handler.begin = lambda *args: False

        collision_handler = game_window.space.add_collision_handler(CollisionType.EnemySlider, CollisionType.Pellet)
        collision_handler.begin = lambda *args: False

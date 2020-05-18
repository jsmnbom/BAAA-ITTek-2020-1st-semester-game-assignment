import pymunk

from . import Actor, resources, CollisionType


class Pellet(Actor):
    """A "Pellet" that the player can pick up to increase their score."""

    def __init__(self, *, pos, batch=None, **kwargs):
        # Make a body and shape for the pellet
        # While the pellet can't move, we still need a shape (and therefore a body) to do proper collision handling
        size = (16, 16)
        mass = 50
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, size, 0)
        shape.collision_type = CollisionType.Pellet
        shape.filter = pymunk.ShapeFilter(categories=CollisionType.Pellet,
                                          mask=pymunk.ShapeFilter.ALL_MASKS ^ CollisionType.EnemyPawn)
        super().__init__(body=body, shape=shape, img=resources.pellet_image, batch=batch, pos=pos, **kwargs)

    def tick(self, dt: float):
        super().tick(dt)
        # Rotate a bit
        self.rotation += 90 * dt

    def on_player_collide(self, game_window):
        """Gets called when a player collides with a pellet."""
        # It takes a little bit for the object to die, don't spawn more than one no matter one
        if not self.dead:
            # When we die then make a new pellet and add 1 to score
            game_window.level.spawn_pellet()
            game_window.ui.score += 1
            self.die()

    @staticmethod
    def init_collision(game_window):
        """Setup collision between pellets and player and enemies"""

        def pre_solve(arbiter, _space, _data):
            """Ignore default collision, and instead call the on_player_collide"""
            arbiter.shapes[1].owner.on_player_collide(game_window)
            return False

        # Call proper on_player_collide (this is a staticmethod, so we need to do shape.owner
        # magic - see Actor - to be able to call a method directly on the collided object).
        collision_handler = game_window.space.add_collision_handler(CollisionType.Player, CollisionType.Pellet)
        collision_handler.pre_solve = pre_solve

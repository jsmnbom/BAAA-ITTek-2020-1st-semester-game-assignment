import random

from pymunk.vec2d import Vec2d
import pymunk

from . import Actor, resources, CollisionType


class Enemy(Actor):
    def __init__(self, *, mass, size, img, speed, pos, player, batch=None, **kwargs):
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        # TODO: Use another shape or even a proper sprite
        shape = pymunk.Poly.create_box(body, size, 1)
        shape.collision_type = CollisionType.Enemy
        super().__init__(body=body, shape=shape, img=img, batch=batch, pos=pos, **kwargs)
        self.speed = speed
        self.player = player

        self.event_handlers = []


class Pawn(Enemy):
    def __init__(self, *, pos, player, batch=None, **kwargs):
        super().__init__(mass=10, size=(32, 32), img=resources.enemy_pawn_image, speed=10, pos=pos, player=player,
                         batch=batch, **kwargs)

    def tick(self, dt: float):
        super().tick(dt)

        vel = Vec2d(self.player.position) - Vec2d(self.position)
        self.body.velocity = vel.normalized() * self.speed

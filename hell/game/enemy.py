import random

from pymunk.vec2d import Vec2d
import pymunk

from . import Actor, resources


class Enemy(Actor):
    def __init__(self, *, pos, player, batch=None, **kwargs):
        mass = 40
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, (32, 32)))
        body.position = pos
        # TODO: Use another shape or even a proper sprite
        shape = pymunk.Poly.create_box(body, (32, 32), 2)
        super().__init__(body=body, shape=shape, img=resources.enemy_image, batch=batch, pos=pos, **kwargs)
        self.speed = 10 + random.randint(0, 5)
        self.player = player

        self.event_handlers = []

    def tick(self, dt: float):
        super().tick(dt)

        vel = Vec2d(self.player.position) - Vec2d(self.position)
        self.body.velocity = vel.normalized() * self.speed

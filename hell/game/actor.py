from pymunk.vec2d import Vec2d
from pyglet.sprite import Sprite
from .game_object import GameObject


class Actor(GameObject, Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.velocity = Vec2d()

    def tick(self, dt: float):
        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt

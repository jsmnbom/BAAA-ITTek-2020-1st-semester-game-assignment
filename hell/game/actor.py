import pymunk
from pymunk.vec2d import Vec2d
from pyglet.sprite import Sprite

from .game_object import GameObject


# We need GameObject first here, which according to python's rules about the MRO and since we were
# careful to put a super().__init__() call in GameObject. __init__() which will then call Sprite.__init__()
class Actor(GameObject, Sprite):
    def __init__(self, *args, body: pymunk.Body, shape: pymunk.Shape, pos, **kwargs):
        pos = Vec2d(pos)
        super().__init__(*args, x=pos.x, y=pos.y, **kwargs)

        self.body = body
        self.shape = shape
        self.shape.owner = self
        self.pos = pos

    def tick(self, dt: float):
        self.x = self.body.position.x
        self.y = self.body.position.y

    @property
    def pos(self) -> Vec2d:
        return self.body.position

    @pos.setter
    def pos(self, value):
        self.body.position = value

    def delete(self):
        super().delete()

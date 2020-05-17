import pymunk
from pymunk.vec2d import Vec2d
from pyglet.sprite import Sprite

from .game_object import GameObject


# We need GameObject first here, which according to python's rules about the MRO and since we were
# careful to put a super().__init__() call in GameObject. __init__() which will then call Sprite.__init__()
class Actor(GameObject, Sprite):
    """A GameObject which is also a sprite and has a physical body and shape."""
    def __init__(self, *args, body: pymunk.Body, shape: pymunk.Shape, pos, **kwargs):
        # Make sure our pos is a vec2d
        pos = Vec2d(pos)
        # Call GameObjects's init which will then call Sprite's.
        super().__init__(*args, x=pos.x, y=pos.y, **kwargs)

        # Store body, shape, and pos
        self.body = body
        self.shape = shape
        self.pos = pos
        # Add a custom owner attribute to shape to make collisions easier
        self.shape.owner = self

    def tick(self, dt: float):
        # Make sure the internal Sprite has the same pos as body
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

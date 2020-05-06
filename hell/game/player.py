import string
import random
from functools import partial
from collections import defaultdict

from pymunk.vec2d import Vec2d
from pyglet.sprite import Sprite
from pyglet.window import key as pyglet_key
from pyglet.text import Label

from . import Actor, resources, WIDTH


class Player(Actor):
    KEY_UP = 0
    KEY_LEFT = 1
    KEY_DOWN = 2
    KEY_RIGHT = 3

    MOVEMENT_DELTAS = {
        KEY_UP: (0, 1),
        KEY_LEFT: (-1, 0),
        KEY_DOWN: (0, -1),
        KEY_RIGHT: (1, 0)
    }

    KEY_LABEL_OFFSETS = {
        KEY_UP: (16, 38),
        KEY_LEFT: (-12, 10),
        KEY_DOWN: (16, -20),
        KEY_RIGHT: (44, 10)
    }

    def __init__(self, *, batch=None, **kwargs):
        super().__init__(img=resources.player_image, batch=batch, **kwargs)
        self.speed = 300

        self.keys = {
            self.KEY_UP: pyglet_key.W,
            self.KEY_LEFT: pyglet_key.A,
            self.KEY_DOWN: pyglet_key.S,
            self.KEY_RIGHT: pyglet_key.D
        }

        self.key_labels = defaultdict(partial(
            Label,
            anchor_x='center',
            anchor_y='center',
            align='center',
            width=32,
            height=32,
            batch=batch
        ))
        self.possible_keys = set(ord(x) for x in (string.digits + string.ascii_lowercase))

        self.key_timer_sprite = Sprite(img=resources.key_timer_image, x=0, y=0, batch=batch)
        self.key_timer_sprite.scale_x = WIDTH / 16

        self.key_timer_max = 5
        self.key_timer = self.key_timer_max
        self.key_directions_randomised = []

        self.key_handler = pyglet_key.KeyStateHandler()
        self.event_handlers = [self.key_timer_sprite, self.key_handler]

    def tick(self, dt: float):
        self.velocity = Vec2d()
        for key, delta in self.MOVEMENT_DELTAS.items():
            if self.key_handler[self.keys[key]]:
                self.velocity += delta

        self.velocity = (self.velocity.normalized() * self.speed)

        super().tick(dt)

        for key in self.MOVEMENT_DELTAS.keys():
            label = self.key_labels[key]
            offset = self.KEY_LABEL_OFFSETS[key]
            label.x = self.x + offset[0]
            label.y = self.y + offset[1]
            label.text = chr(self.keys[key]).upper()

        self.key_timer -= 1 * dt
        self.key_timer_sprite.scale_x = (WIDTH * (self.key_timer / self.key_timer_max)) / 16

        if self.key_timer <= 0:
            self.key_timer = self.key_timer_max
            self.randomise_movement_keys(1)

    def randomise_movement_keys(self, i: int):
        for _ in range(i):
            if not self.key_directions_randomised:
                self.key_directions_randomised = list(self.MOVEMENT_DELTAS.keys())
                random.shuffle(self.key_directions_randomised)

            direction = self.key_directions_randomised.pop()
            self.keys[direction] = random.choice(tuple(self.possible_keys - set(self.keys.values())))

    def delete(self):
        for label, _ in self.key_labels:
            label.delete()
        self.key_timer_sprite.delete()
        super().delete()

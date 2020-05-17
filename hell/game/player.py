import string
import random
import math
from functools import partial
from collections import defaultdict

from pymunk.vec2d import Vec2d
from pyglet.sprite import Sprite
from pyglet.window import key as pyglet_key
from pyglet.text import Label
import pymunk
import pytweening

from . import Actor, resources, WIDTH, CollisionType, blink


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
        KEY_UP: (1, 28),
        KEY_LEFT: (-26, 0),
        KEY_DOWN: (1, -30),
        KEY_RIGHT: (28, 0)
    }

    def __init__(self, *, pos, player_batch=None, ui_batch=None, **kwargs):
        size = (32, 32)
        mass = 50
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        # TODO: Use another shape or even a proper sprite
        shape = pymunk.Poly.create_box(body, size, 2)
        shape.collision_type = CollisionType.Player
        super().__init__(body=body, shape=shape, img=resources.player_image, batch=player_batch, pos=pos, **kwargs)
        self.speed = 40

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
            font_size=24,
            font_name='m5x7',
            batch=ui_batch,
        ))
        self.possible_keys = set(ord(x) for x in (string.digits + string.ascii_lowercase))

        self.key_timer_max = 5
        self.key_timer = self.key_timer_max
        self.key_directions_randomised = []
        self.next_direction = self._get_next_direction()

        self.key_handler = pyglet_key.KeyStateHandler()
        self.event_handlers = [self.key_handler]

    def tick(self, dt: float):
        super().tick(dt)

        vel = Vec2d()
        for key, delta in self.MOVEMENT_DELTAS.items():
            if self.key_handler[self.keys[key]]:
                vel += delta

        self.body.velocity = vel.normalized() * self.speed

        for key in self.MOVEMENT_DELTAS.keys():
            label = self.key_labels[key]
            offset = self.KEY_LABEL_OFFSETS[key]
            label.x = self.x + offset[0]
            label.y = self.y + offset[1]
            label.text = chr(self.keys[key]).upper()

        self.key_timer -= 1 * dt

        if self.key_timer <= 0:
            self.key_timer = self.key_timer_max
            self._randomise_movement_key()
            for key in self.MOVEMENT_DELTAS.keys():
                label = self.key_labels[key]
                label.color = (255, 255, 255, 255)

        next_key_blink_start = 1.5
        next_key_blink_interval = 0.5
        if self.key_timer < next_key_blink_start:
            next_key_blink = math.fmod(self.key_timer, next_key_blink_interval)
            self.key_labels[self.next_direction].color = blink(next_key_blink, pytweening.easeInCubic,
                                                               pytweening.easeOutCubic, next_key_blink_interval,
                                                               (255, 255, 255))

    def _randomise_movement_key(self):
        self.keys[self.next_direction] = random.choice(tuple(self.possible_keys - set(self.keys.values())))
        self.next_direction = self._get_next_direction()

    def _get_next_direction(self):
        if not self.key_directions_randomised:
            self.key_directions_randomised = list(self.MOVEMENT_DELTAS.keys())
            random.shuffle(self.key_directions_randomised)

        return self.key_directions_randomised.pop()

    def delete(self):
        for key in self.MOVEMENT_DELTAS.keys():
            label = self.key_labels[key]
            label.delete()
        super().delete()

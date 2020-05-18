import string
import random
import math
from functools import partial
from collections import defaultdict

from pymunk.vec2d import Vec2d
from pyglet.window import key as pyglet_key
from pyglet.text import Label
import pymunk
import pytweening

from . import Actor, resources, CollisionType, blink


class Player(Actor):
    """The player actor. Controlled by the keyboard."""
    # Constants for the keys to move in a certain direction
    KEY_UP = 0
    KEY_LEFT = 1
    KEY_DOWN = 2
    KEY_RIGHT = 3

    # How to move for each key
    MOVEMENT_DELTAS = {
        KEY_UP: (0, 1),
        KEY_LEFT: (-1, 0),
        KEY_DOWN: (0, -1),
        KEY_RIGHT: (1, 0)
    }

    # Offsets of where to show the labels for which key to press
    # they are a bit funky due to how text sizes can vary
    KEY_LABEL_OFFSETS = {
        KEY_UP: (1, 28),
        KEY_LEFT: (-26, 0),
        KEY_DOWN: (1, -30),
        KEY_RIGHT: (28, 0)
    }

    def __init__(self, *, pos, player_batch=None, ui_batch=None, **kwargs):
        # Assign a body and shape
        size = (32, 32)
        mass = 50
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, size, 2)
        shape.collision_type = CollisionType.Player
        shape.filter = pymunk.ShapeFilter(categories=CollisionType.Player,
                                          mask=pymunk.ShapeFilter.ALL_MASKS ^ CollisionType.WallSensor)
        super().__init__(body=body, shape=shape, img=resources.player_image, batch=player_batch, pos=pos, **kwargs)
        # Speed that is slightly higher than EnemyPawn but slower than EnemySlider
        self.speed = 40

        # Current keys that when pressed move in a certain direction
        self.keys = {
            self.KEY_UP: pyglet_key.W,
            self.KEY_LEFT: pyglet_key.A,
            self.KEY_DOWN: pyglet_key.S,
            self.KEY_RIGHT: pyglet_key.D
        }

        # Label for each key
        # This is a defaultdict with a partial, simply so we don't need to init the dictionary ourselves
        # As soon as self.key_labels[KEY_LEFT] is accessed the label will be created
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
        # The keys that are allowed as movement keys
        # A-Z + 0-9
        self.possible_keys = set(ord(x) for x in (string.digits + string.ascii_lowercase))

        # Reset the key_timer to this value when it reaches 0
        # Effectively how often (in sec) to randomize a key
        self.key_timer_min = 5
        self.key_timer_max = 15
        # Timer that goes down and when reaches 0 a key will be randomized
        self.key_timer = random.randrange(self.key_timer_min, self.key_timer_max)
        # A list of directions (up, left, right, down) but randomized
        # This allows us to, instead of just picking a a random direction,
        # we make sure that all the directions are chosen with equal frequency
        self.key_directions_randomised = []
        # The next direction key that will change
        # We need this so we can blink the label right before the key changes
        self.next_direction = self._get_next_direction()

        # The key handler will remember which keys are pressed/released
        self.key_handler = pyglet_key.KeyStateHandler()
        self.event_handlers = [self.key_handler]

    def tick(self, dt: float):
        super().tick(dt)

        # For each movement key
        vel = Vec2d()
        for key, delta in self.MOVEMENT_DELTAS.items():
            # If it's held down
            if self.key_handler[self.keys[key]]:
                # Add it's movement delta to our velocity
                vel += delta

        # Then make sure the velocity is normalized (so we always move the same speed even diagonally)
        self.body.velocity = vel.normalized() * self.speed

        # For each movement key
        for key in self.MOVEMENT_DELTAS.keys():
            # Update the label position
            label = self.key_labels[key]
            offset = self.KEY_LABEL_OFFSETS[key]
            label.x = self.x + offset[0]
            label.y = self.y + offset[1]
            # And also the label text, making sure the key is played as uppercase
            label.text = chr(self.keys[key]).upper()

        # Decrease the key timer by a 1 each second
        self.key_timer -= 1 * dt

        # If the key timer has reached 0
        if self.key_timer <= 0:
            # Reset the timer
            self.key_timer = random.randrange(self.key_timer_min, self.key_timer_max)
            # Randomize the key
            self._randomise_movement_key()
            # Then make sure all the labels are visible
            # Due to how the blink works, and small differences in the FPS of the game, this is required
            for key in self.MOVEMENT_DELTAS.keys():
                label = self.key_labels[key]
                label.color = (255, 255, 255, 255)

        # Start blinking when there's 1.5 sec until the key will change
        next_key_blink_start = 1.5
        # Fully blink in and out every 0,5 sec
        next_key_blink_interval = 0.5
        if self.key_timer < next_key_blink_start:
            # Figure out actual blink interval, by float mod
            next_key_blink = math.fmod(self.key_timer, next_key_blink_interval)
            # Then set the color (alpha) of the key to be blinking
            self.key_labels[self.next_direction].color = blink(next_key_blink, pytweening.easeInCubic,
                                                               pytweening.easeOutCubic, next_key_blink_interval,
                                                               (255, 255, 255))

    def _randomise_movement_key(self):
        # Pick a key from a the possible keys as long as we're not already using it
        self.keys[self.next_direction] = random.choice(tuple(self.possible_keys - set(self.keys.values())))
        # Then get a new direction for the next key to change
        self.next_direction = self._get_next_direction()

    def _get_next_direction(self):
        # If we are out of keys in the list
        if not self.key_directions_randomised:
            # Then get a list of keys
            self.key_directions_randomised = list(self.MOVEMENT_DELTAS.keys())
            # And randomize the order
            random.shuffle(self.key_directions_randomised)

        # Just take the left item in the list and remove and return it
        return self.key_directions_randomised.pop()

    def delete(self):
        # Make sure we delete our children
        for key in self.MOVEMENT_DELTAS.keys():
            label = self.key_labels[key]
            label.delete()
        super().delete()

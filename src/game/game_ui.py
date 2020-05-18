import math

from pyglet.sprite import Sprite
from pyglet.text import Label
from pymunk.vec2d import Vec2d
import pymunk

from . import GameObject, WIDTH, HEIGHT, resources, valmap, Player, CollisionType


class GameUI(GameObject):
    """In game UI that shows score etc."""

    def __init__(self, *, player: Player, space: pymunk.Space, ui_batch=None, background_batch=None):
        super().__init__()

        self.player = player
        self.space = space
        self.background_batch = background_batch

        self.danger_sprite = Sprite(img=resources.danger_image, batch=background_batch, x=128, y=128)
        self.danger_sprite.visible = False

        # Internal score modified by the property below
        self._score = 0
        # Show the score
        self.score_label = Label(
            '',
            font_name='m5x7',
            font_size=48,
            x=WIDTH - 10,
            y=HEIGHT,
            anchor_x='right',
            anchor_y='top',
            batch=ui_batch
        )
        # "call" the property setter below
        self.score = self._score

    def tick(self, dt: float):
        # Don't show danger sprite by default
        self.danger_sprite.visible = False
        # Okay so to find out where to possibly show the danger sprite
        # We need to do a ray cast from the center of the map to the player
        # And when we hit a wall, that is where it would be shown if it is close enough to the player
        # The reason we need this, is that the logic for snapping from the players position to a wall position
        # without raycasting in the case of corners (where two walls meet) is quite complicated so this is simply easier

        # get some preliminary start and end points
        start = Vec2d(WIDTH, HEIGHT) / 2
        end = (self.player.pos - start)
        # We can't divide by 0, so make sure the player has moved away from the center
        if end.get_length_sqrd() > 0:
            # Then set the length to be the diagonal of the screen, so that the ray will always hit a wall somewhere
            end.length = math.sqrt(WIDTH ** 2 + HEIGHT ** 2)
            # Remove the start as we don't want vector relative to the center of the screen but rather proper coords
            end += start
            # Raycast, finding only wall sensors
            results = self.space.segment_query(start, end, 1, pymunk.ShapeFilter(mask=CollisionType.WallSensor))
            # If we hit something
            if results:
                # Find our distance to it
                wall_result = results[0]
                distance = (self.player.pos - wall_result.point).length
                # And if our distance is less than half of danger_sprite's width/height
                if distance < self.danger_sprite.width / 2:
                    # Show the sprite with increasing opacity as player nears wall
                    self.danger_sprite.visible = True
                    self.danger_sprite.opacity = min(valmap(distance, self.danger_sprite.width / 2, 0, 0, 255), 255)
                    self.danger_sprite.x = wall_result.point.x
                    self.danger_sprite.y = wall_result.point.y

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        # Update the label text with the new score
        self.score_label.text = f'Score: {self._score}'

    def delete(self):
        self.score_label.delete()
        self.danger_sprite.delete()
        super().delete()

from pyglet.sprite import Sprite
from pyglet.text import Label

from . import GameObject, WIDTH, HEIGHT, resources


class GameUI(GameObject):
    def __init__(self, *, player, ui_batch=None, overlay_batch=None):
        super().__init__()

        self.player = player

        self._score = 0
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
        self.score = self._score

        # self.overlay = Sprite(resources.overlay_image, batch=overlay_batch)
        # self.overlay.color = (150, 0, 0)
        # self.overlay.opacity = 25

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self.score_label.text = f'Score: {self._score}'

    def delete(self):
        self.score_label.delete()

    # def tick(self, dt: float):
    #     min_wall_distance = min([self.player.x, WIDTH - self.player.x, self.player.y, HEIGHT - self.player.y])
    #     if min_wall_distance < 100:
    #         self.overlay.opacity = 155 - (min_wall_distance / 100) * (155 - 25)
    #     else:
    #         self.overlay.opacity = 25

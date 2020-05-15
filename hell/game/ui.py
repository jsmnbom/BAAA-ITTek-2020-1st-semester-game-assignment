from pyglet.text import Label

from . import GameObject, WIDTH, HEIGHT


class UI(GameObject):
    def __init__(self, *, batch):
        super().__init__()
        self._score = 0
        self.score_label = Label(
            '',
            font_name='m5x7',
            font_size=48,
            x=WIDTH - 10,
            y=HEIGHT,
            anchor_x='right',
            anchor_y='top',
            batch=batch
        )
        self.score = self._score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self.score_label.text = f'Score: {self._score}'

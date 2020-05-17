from pyglet.text import Label

from . import GameObject, WIDTH, HEIGHT


class GameUI(GameObject):
    """In game UI that shows score etc."""

    def __init__(self, *, player, ui_batch=None, overlay_batch=None):
        super().__init__()

        self.player = player

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
        super().delete()

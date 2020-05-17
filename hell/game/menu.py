from pyglet.text import Label
from pyglet.window import key
from pyglet.text.caret import Caret
from pyglet.text.layout import IncrementalTextLayout
from pyglet.text.document import UnformattedDocument
import pytweening

from . import GameObject, WIDTH, HEIGHT, blink


class Menu(GameObject):
    def __init__(self, *, highscores, ui_batch, cb_start_game=None, cb_add_highscore=None, add_score=None):
        super().__init__()

        self.event_handlers = [self]

        self.cb_start_game = cb_start_game
        self.cb_add_highscore = cb_add_highscore
        self.ui_batch = ui_batch
        self.add_score = add_score

        self.children = []

        self.children.append(Label(
            'WELCOME TO',
            font_name='m5x7',
            font_size=128,
            x=WIDTH / 2,
            y=HEIGHT - 16,
            anchor_x='center',
            anchor_y='top',
            bold=False,
            batch=self.ui_batch
        ))

        self.children.append(Label(
            'HELL',
            font_name='m5x7',
            font_size=512,
            x=WIDTH / 2 + 50,
            y=HEIGHT,
            anchor_x='center',
            anchor_y='top',
            bold=False,
            batch=self.ui_batch
        ))

        if add_score is not None:
            self.continue_label = None

            self.children.append(Label(
                'Your score was:',
                font_name='m5x7',
                font_size=48,
                x=WIDTH / 2,
                y=400,
                align='center',
                anchor_x='center',
                anchor_y='bottom',
                batch=self.ui_batch
            ))
            self.children.append(Label(
                f'{add_score}',
                font_name='m5x7',
                font_size=128,
                x=WIDTH / 2,
                y=280,
                align='center',
                anchor_x='center',
                anchor_y='bottom',
                batch=self.ui_batch
            ))
            self.children.append(Label(
                'Enter name for highscore:',
                font_name='m5x7',
                font_size=32,
                x=WIDTH / 2,
                y=200,
                align='center',
                anchor_x='center',
                anchor_y='bottom',
                batch=self.ui_batch
            ))

            self.document = UnformattedDocument()
            self.document.set_style(0, 1, {
                'font_name': 'm5x7',
                'font_size': 64,
                'color': (255, 255, 255, 255),
                'align': 'center'
            })
            font = self.document.get_font()
            height = font.ascent - font.descent
            self.layout = IncrementalTextLayout(self.document, WIDTH / 3, height, multiline=True, batch=self.ui_batch)
            self.layout.anchor_y = 'top'
            self.layout.anchor_x = 'center'
            self.layout.x = WIDTH / 2
            self.layout.y = 200
            self.caret = Caret(self.layout, batch=self.ui_batch, color=(255, 255, 255))
            self.caret.on_text('q')
            self.caret.on_text_motion(key.MOTION_BACKSPACE)
            self.children.append(self.layout)
            self.children.append(self.caret)
        else:
            if highscores:
                self.children.append(Label(
                    'Highscores:',
                    font_name='m5x7',
                    font_size=48,
                    x=WIDTH / 2,
                    y=420,
                    align='center',
                    anchor_x='center',
                    anchor_y='bottom',
                    batch=self.ui_batch
                ))
                for i, highscore in enumerate(highscores):
                    self.children.append(Label(
                        f'{highscore.name} - {highscore.score}',
                        font_name='m5x7',
                        font_size=32,
                        x=WIDTH / 2,
                        y=380 - i * 32,
                        align='center',
                        anchor_x='center',
                        anchor_y='bottom',
                        batch=self.ui_batch
                    ))

            self.continue_label = Label(
                'Press SPACE to start game...',
                font_name='m5x7',
                font_size=48,
                x=WIDTH / 2,
                y=32 if highscores else HEIGHT / 4,
                align='center',
                anchor_x='center',
                anchor_y='bottom',
                batch=self.ui_batch
            )
            self.continue_timer = 0

            self.children.append(self.continue_label)

    def tick(self, dt: float):
        if self.continue_label:
            self.continue_timer += dt
            if self.continue_timer > 2:
                self.continue_timer = 0
            self.continue_label.color = blink(self.continue_timer, pytweening.easeInCubic, pytweening.easeOutCubic, 2,
                                              (255, 255, 255))

    def delete(self):
        for child in self.children:
            child.delete()

    def on_key_release(self, symbol, modifier):
        if self.add_score is None:
            if symbol == key.SPACE:
                self.cb_start_game()
        else:
            if symbol == key.ENTER:
                self.cb_add_highscore(self.document.text, self.add_score)

    def on_text(self, text):
        if self.add_score is not None:
            text = text.replace('\r', '\n')
            if text != '\n':
                self.caret.on_text(text)
                if self.layout.lines[0].width + 20 > self.layout.width:
                    self.caret.on_text_motion(key.MOTION_BACKSPACE)

    def on_text_motion(self, motion, select=False):
        if self.add_score is not None:
            self.caret.on_text_motion(motion, select)

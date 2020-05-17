from pyglet.text import Label
from pyglet.window import key
from pyglet.text.caret import Caret
from pyglet.text.layout import IncrementalTextLayout
from pyglet.text.document import UnformattedDocument
import pytweening

from . import GameObject, WIDTH, HEIGHT, blink


class Menu(GameObject):
    """Provides menus for the game. Both main menu with highscores and a menu to input name for highscore.

    Which menu is shown depends on add_score. If it's None then main menu is shown."""
    def __init__(self, *, highscores, ui_batch, cb_start_game=None, cb_add_highscore=None, add_score=None):
        super().__init__()

        # Make sure we can handle events
        self.event_handlers = [self]

        # Store callbacks, the ui batch and our optional score3
        self.cb_start_game = cb_start_game
        self.cb_add_highscore = cb_add_highscore
        self.ui_batch = ui_batch
        self.add_score = add_score

        # We need to keep track of our children so we can remove them in self.delete()
        self.children = []

        # Show title
        self.children.append(Label(
            'WELCOME TO',
            font_name='m5x7',
            font_size=128,
            x=WIDTH / 2,
            y=HEIGHT - 16,
            anchor_x='center',
            anchor_y='top',
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
            batch=self.ui_batch
        ))

        # If we need to add a score
        if add_score is not None:
            # Make sure that self.continue_label exists so we don't crash in self.tick()
            self.continue_label = None

            # Show some text
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

            # Prepare a document with styling
            self.document = UnformattedDocument()
            self.document.set_style(0, 1, {
                'font_name': 'm5x7',
                'font_size': 64,
                'color': (255, 255, 255, 255),
                'align': 'center'
            })
            # Find the height of the font
            font = self.document.get_font()
            height = font.ascent - font.descent
            # Make a TextLayout that handles dynamically adding text
            # Make it multiline even though we don't want multiple lines because otherwise align=center doesn't work
            self.layout = IncrementalTextLayout(self.document, WIDTH / 3, height, multiline=True, batch=self.ui_batch)
            self.layout.anchor_y = 'top'
            self.layout.anchor_x = 'center'
            self.layout.x = WIDTH / 2
            self.layout.y = 200
            # Add a carat (cursor)
            self.caret = Caret(self.layout, batch=self.ui_batch, color=(255, 255, 255))
            # Type q and then backspace
            # This ensures that the carat is visible as it only shows up after something has been typed
            self.caret.on_text('q')
            self.caret.on_text_motion(key.MOTION_BACKSPACE)
            # Make sure we can delete layout and carat in self.delete()
            self.children.append(self.layout)
            self.children.append(self.caret)
        else:
            # If we have some highscores to show
            if highscores:
                # Show a title
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
                # ... followed by each highscore
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

            # Show continue label, and make sure to have it below highscores if any
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
            # Timer for blinking
            self.continue_timer = 0

            self.children.append(self.continue_label)

    def tick(self, dt: float):
        # If we have a continue label then blink it
        if self.continue_label:
            self.continue_timer += dt
            if self.continue_timer > 2:
                self.continue_timer = 0
            self.continue_label.color = blink(self.continue_timer, pytweening.easeInCubic, pytweening.easeOutCubic, 2,
                                              (255, 255, 255))

    def delete(self):
        # Make sure to also delete our children
        for child in self.children:
            child.delete()
        super().delete()

    def on_key_release(self, symbol, modifier):
        if self.add_score is None:
            # If we are not adding a score then if space was pressed, start the game
            if symbol == key.SPACE:
                self.cb_start_game()
        else:
            # If we are adding a score then when enter is pressed, submit
            # that highscore (which will then also go to next menu screen)
            if symbol == key.ENTER:
                self.cb_add_highscore(self.document.text, self.add_score)

    def on_text(self, text):
        if self.add_score is not None:
            # Make sure we don't add any newlines (layout is multiline but we never want more than 1 line)
            text = text.replace('\r', '\n')
            if text != '\n':
                # Add the text to the caret
                self.caret.on_text(text)
                # If the text is too long then send a backspace to delete last char
                if self.layout.lines[0].width + 20 > self.layout.width:
                    self.caret.on_text_motion(key.MOTION_BACKSPACE)

    def on_text_motion(self, motion, select=False):
        if self.add_score is not None:
            # Forward text motions to the caret
            self.caret.on_text_motion(motion, select)

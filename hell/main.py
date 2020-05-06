import pyglet
from pyglet import clock
from pyglet.window import Window, FPSDisplay
from pyglet.graphics import Batch

from hell.game import TPS, WIDTH, HEIGHT


# noinspection PyAbstractClass
class GameWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_batch = Batch()

        self.fps_display = FPSDisplay(window=self)

        clock.schedule_interval(self.tick, 1 / TPS)

    def tick(self, dt: float):
        pass

    def on_draw(self):
        self.clear()
        self.main_batch.draw()
        self.fps_display.draw()


def main():
    game_window = GameWindow(width=WIDTH, height=HEIGHT)
    game_window.reset()
    pyglet.app.run()


if __name__ == "__main__":
    main()

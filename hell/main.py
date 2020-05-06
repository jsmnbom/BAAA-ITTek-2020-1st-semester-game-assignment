from typing import List

from pyglet.app import run as pyglet_run
from pyglet import clock
from pyglet.window import Window, FPSDisplay
from pyglet.graphics import Batch

from hell.game import TPS, WIDTH, HEIGHT, Player, GameObject


# noinspection PyAbstractClass
class GameWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.objects: List[GameObject] = []
        self.main_batch = Batch()

        self.fps_display = FPSDisplay(window=self)

        clock.schedule_interval(self.tick, 1 / TPS)

    def reset(self):
        try:
            while True:
                self.pop_handlers()
        except Exception as e:
            print(e)

        player = Player(x=self.width / 2, y=self.height / 2, batch=self.main_batch)

        self.objects = [player]

        for obj in self.objects:
            for handler in obj.event_handlers:
                self.push_handlers(handler)

    def tick(self, dt: float):
        to_add = []

        for obj in self.objects:
            obj.tick(dt)
            to_add.extend(obj.new_objects)
            obj.new_objects = []

        for to_remove in [obj for obj in self.objects if obj.dead]:
            to_add.extend(to_remove.new_objects)
            to_remove.delete()
            self.objects.remove(to_remove)

        self.objects.extend(to_add)

    def on_draw(self):
        self.clear()
        self.main_batch.draw()
        self.fps_display.draw()


def main():
    game_window = GameWindow(width=WIDTH, height=HEIGHT)
    game_window.reset()
    pyglet_run()


if __name__ == "__main__":
    main()

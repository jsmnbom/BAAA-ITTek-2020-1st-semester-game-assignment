from typing import List

from pyglet.app import run as pyglet_run
from pyglet import clock
from pyglet.window import Window, FPSDisplay
from pyglet.graphics import Batch
import pymunk

from hell.game import TPS, WIDTH, HEIGHT, Player, GameObject, CollisionType, Level, Slider, Enemy, UI, Pellet


# noinspection PyAbstractClass
class GameWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.objects: List[GameObject] = []
        self.main_batch = Batch()
        self.player_batch = Batch()

        self.fps_display = FPSDisplay(window=self)

        clock.schedule_interval(self.tick, 1 / TPS)

        # Vars assigned to later in self.reset
        self.space = None
        self.player = None
        self.level = None
        self.ui = None

    @staticmethod
    def cancel_collision(arbiter, space, data):
        return False

    def reset(self):
        # Clear handlers
        try:
            while True:
                self.pop_handlers()
        except Exception as e:
            print(e)
        # Clear space
        self.space = pymunk.Space()
        # Remove objects
        for obj in self.objects:
            obj.delete()
        self.objects = []

        self.player = Player(pos=(self.width / 2, self.height / 2), batch=self.player_batch)
        self._add_game_object(self.player)

        self.level = Level(player=self.player, batch=self.main_batch)
        self._add_game_object(self.level)

        self.ui = UI(batch=self.main_batch)
        self._add_game_object(self.ui)

        self._add_walls()

        Pellet.init_collision(self)
        Enemy.init_collision(self)
        Slider.init_collision(self)

    def _add_walls(self):
        static_body = self.space.static_body
        walls = [
            pymunk.Segment(static_body, (0, 0), (WIDTH, 0), 0.0),
            pymunk.Segment(static_body, (WIDTH, 0), (WIDTH, HEIGHT), 0.0),
            pymunk.Segment(static_body, (WIDTH, HEIGHT), (0, HEIGHT), 0.0),
            pymunk.Segment(static_body, (0, HEIGHT), (0, 0), 0.0)
        ]
        for wall in walls:
            self.space.add(wall)
            wall.collision_type = CollisionType.Wall

        collision_handler = self.space.add_collision_handler(CollisionType.Player, CollisionType.Wall)
        collision_handler.post_solve = lambda *_: self.reset()

    def tick(self, dt: float):
        to_add: List[GameObject] = []

        # Tick each object and collect new objects they may have spawned
        for obj in self.objects:
            obj.tick(dt)
            to_add.extend(obj.new_objects)
            obj.new_objects = []

        for to_remove in [obj for obj in self.objects if obj.dead]:
            # If it has custom deleting routine (like pyglet's sprites)
            if hasattr(to_remove, 'delete'):
                to_remove.delete()
            # Remove our tracking of the object
            self.objects.remove(to_remove)

        # Add new objects
        for obj in to_add:
            self._add_game_object(obj)

        # Run physics in overdrive to get proper segment collision at high velocity
        for i in range(10):
            self.space.step(dt)

    def _add_game_object(self, obj: GameObject):
        self.objects.append(obj)
        for handler in obj.event_handlers:
            self.push_handlers(handler)
        if hasattr(obj, 'body'):
            self.space.add(obj.body)
        if hasattr(obj, 'shape'):
            self.space.add(obj.shape)

    def on_draw(self):
        self.clear()
        self.main_batch.draw()
        self.player_batch.draw()
        self.fps_display.draw()


def main():
    game_window = GameWindow(width=WIDTH, height=HEIGHT)
    game_window.reset()
    pyglet_run()


if __name__ == "__main__":
    main()

from typing import List

from pyglet.app import run as pyglet_run
from pyglet import clock
from pyglet.window import Window, FPSDisplay
from pyglet.graphics import Batch
import pymunk

from hell.game import TPS, WIDTH, HEIGHT, Player, GameObject, Enemy, CollisionType


# noinspection PyAbstractClass
class GameWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.objects: List[GameObject] = []
        self.to_add: List[GameObject] = []
        self.main_batch = Batch()

        self.fps_display = FPSDisplay(window=self)

        clock.schedule_interval(self.tick, 1 / TPS)

        # Vars assigned to later
        self.space = None
        self.player = None

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
        # And finally clear all the objects
        self.objects = []

        self.player = Player(pos=(self.width / 2, self.height / 2), batch=self.main_batch)
        self._add_game_object(self.player)

        self._add_walls()

        clock.unschedule(self._add_random_enemy)
        clock.schedule_interval(self._add_random_enemy, 1)

    def _add_random_enemy(self, *args):
        self.to_add.append(Enemy(pos=(100, 100), player=self.player, batch=self.main_batch))

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

        wall_player_collision_handler = self.space.add_collision_handler(CollisionType.Player, CollisionType.Wall)
        wall_player_collision_handler.post_solve = lambda *args: self.reset()

    def tick(self, dt: float):
        for obj in self.objects:
            obj.tick(dt)
            self.to_add.extend(obj.new_objects)
            obj.new_objects = []

        for to_remove in [obj for obj in self.objects if obj.dead]:
            self.to_add.extend(to_remove.new_objects)
            to_remove.delete()
            self.objects.remove(to_remove)

        for obj in self.to_add:
            self._add_game_object(obj)
        self.to_add = []
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
        self.fps_display.draw()


def main():
    game_window = GameWindow(width=WIDTH, height=HEIGHT)
    game_window.reset()
    pyglet_run()


if __name__ == "__main__":
    main()

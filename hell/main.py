import os
import pickle
from typing import List
from collections import namedtuple

from pyglet import clock, resource
from pyglet.app import run as pyglet_run
from pyglet.window import Window, FPSDisplay
from pyglet.graphics import Batch
import pymunk

from hell.game import (TPS, WIDTH, HEIGHT, Player, GameObject, CollisionType, Level, EnemyPawn, EnemySlider, GameUI,
                       Pellet, Menu)

Highscore = namedtuple('Highscore', 'name, score')


# noinspection PyAbstractClass
class GameWindow(Window):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.objects: List[GameObject] = []
        self.main_batch = Batch()
        self.player_batch = Batch()
        self.ui_batch = Batch()
        self.overlay_batch = Batch()

        self.fps_display = FPSDisplay(window=self)

        clock.schedule_interval(self.tick, 1 / TPS)

        settings_dir = resource.get_settings_path('WelcomeToHell')
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)
        self.highscores_filename = os.path.join(settings_dir, "highscores.pickle")
        try:
            with open(self.highscores_filename, "rb") as f:
                self.highscores = pickle.load(f)
            self.highscores.sort(key=lambda highscore: highscore.score, reverse=True)
        except (OSError, IOError):
            self.highscores = []

        # Vars assigned to later in self.reset
        self.space = None
        self.player = None
        self.level = None
        self.ui = None
        self.menu = None

    def save_highscores(self):
        with open(self.highscores_filename, "wb") as f:
            pickle.dump(self.highscores, f)

    def main_menu(self, add_score=None):
        self.reset()

        if add_score is not None:
            def add_highscore(name, score):
                if len(self.highscores) < 10 or score >= self.highscores[-1].score:
                    self.highscores.append(Highscore(name, score))
                    self.highscores.sort(key=lambda highscore: highscore.score, reverse=True)
                    if len(self.highscores) > 9:
                        self.highscores.pop()
                    self.save_highscores()
                self.main_menu()

            self.menu = Menu(highscores=self.highscores, ui_batch=self.ui_batch, cb_start_game=self.start_game,
                             add_score=add_score, cb_add_highscore=add_highscore)
        else:
            self.menu = Menu(highscores=self.highscores, ui_batch=self.ui_batch, cb_start_game=self.start_game)
        self._add_game_object(self.menu)

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

    def start_game(self):
        self.reset()

        self.player = Player(pos=(self.width / 2, self.height / 2), player_batch=self.player_batch,
                             ui_batch=self.ui_batch)
        self._add_game_object(self.player)

        self.level = Level(player=self.player, batch=self.main_batch)
        self._add_game_object(self.level)

        self.ui = GameUI(player=self.player, ui_batch=self.ui_batch, overlay_batch=self.overlay_batch)
        self._add_game_object(self.ui)

        self._add_walls()

        Pellet.init_collision(self)
        EnemyPawn.init_collision(self)
        EnemySlider.init_collision(self)

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
        collision_handler.post_solve = lambda *_: self.main_menu(add_score=self.ui.score)

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
        self.ui_batch.draw()
        self.overlay_batch.draw()
        self.fps_display.draw()


def main():
    game_window = GameWindow(width=WIDTH, height=HEIGHT)
    game_window.main_menu()
    pyglet_run()


if __name__ == "__main__":
    main()

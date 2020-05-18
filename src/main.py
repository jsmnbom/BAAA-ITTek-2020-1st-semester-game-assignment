import os
import pickle
from typing import List
from collections import namedtuple

from pyglet import clock, resource
from pyglet.app import run as pyglet_run
from pyglet.window import Window, FPSDisplay
from pyglet.graphics import Batch
import pymunk

from src.game import (TPS, WIDTH, HEIGHT, Player, GameObject, CollisionType, Level, EnemyPawn, EnemySlider, GameUI,
                      Pellet, Menu)

# A highscore object, easier to sort than having the data in a dict
Highscore = namedtuple('Highscore', 'name, score')


# noinspection PyAbstractClass
class GameWindow(Window):
    """Main game window."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # List of current objects that we know of
        self.objects: List[GameObject] = []
        # Batches for efficient drawing (each batch can be drawn at once
        # instead of needing to draw every single object individually)
        self.main_batch = Batch()
        self.player_batch = Batch()
        self.ui_batch = Batch()
        self.overlay_batch = Batch()

        # FPS display in bottom left corner
        self.fps_display = FPSDisplay(window=self)

        # Call self.tick() approx 60 times a sec
        clock.schedule_interval(self.tick, 1 / TPS)

        # Locate setting directory
        # This will be somewhere in AppData on windows and ~/.config on linux etc.
        settings_dir = resource.get_settings_path('WelcomeToHell')
        # Make sure it exists otherwise create it
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        self.highscores_filename = os.path.join(settings_dir, "highscores.pickle")
        # Try loading our highscores or assume we have done if we fail
        try:
            with open(self.highscores_filename, "rb") as f:
                self.highscores = pickle.load(f)
            # Sort the highscores just to be safe
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
        """Saves self.highscores to self.highscores_filename."""
        with open(self.highscores_filename, "wb") as f:
            pickle.dump(self.highscores, f)

    def main_menu(self, add_score=None):
        """Shows the main menu (or a prompt for highscore name if add_score != None)"""
        # Start by clearing everything
        self.reset()

        # If we have a score we need to add
        if add_score is not None:
            # Inner function that acts as callback for the menu when the player has entered their name
            def add_highscore(name, score):
                # If we don't have 10 scores yet or the score if higher than the lowest one
                if len(self.highscores) < 10 or score >= self.highscores[-1].score:
                    # Add the highscore and sort them
                    self.highscores.append(Highscore(name, score))
                    self.highscores.sort(key=lambda highscore: highscore.score, reverse=True)
                    # If we have more than 9 then remove the last one
                    if len(self.highscores) > 9:
                        self.highscores.pop()
                    # Save the highscores to make
                    self.save_highscores()
                # Go back to main menu
                self.main_menu()

            self.menu = Menu(highscores=self.highscores, ui_batch=self.ui_batch,
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
        # Start by clearing everything
        self.reset()

        # Create a player in the middle of the window
        self.player = Player(pos=(self.width / 2, self.height / 2), player_batch=self.player_batch,
                             ui_batch=self.ui_batch)
        self._add_game_object(self.player)

        # Add a level that controls enemy and pellet spawning
        self.level = Level(player=self.player, batch=self.main_batch)
        self._add_game_object(self.level)

        # Add UI which is only the score for now
        self.ui = GameUI(player=self.player, ui_batch=self.ui_batch, overlay_batch=self.overlay_batch)
        self._add_game_object(self.ui)

        # Add walls on window edges
        self._add_walls()

        # Initialize collisions
        Pellet.init_collision(self)
        EnemyPawn.init_collision(self)
        EnemySlider.init_collision(self)

    def _add_walls(self):
        """Adds four walls on window edges."""
        # Walls are static (ie they don't move)
        static_body = self.space.static_body
        walls = [
            pymunk.Segment(static_body, (-32, -32), (WIDTH + 32, -32), 0.0),
            pymunk.Segment(static_body, (WIDTH + 32, -32), (WIDTH + 32, HEIGHT + 32), 0.0),
            pymunk.Segment(static_body, (WIDTH + 32, HEIGHT + 32), (-32, HEIGHT + 32), 0.0),
            pymunk.Segment(static_body, (-32, HEIGHT + 32), (-32, -32), 0.0)
        ]
        for wall in walls:
            self.space.add(wall)
            wall.collision_type = CollisionType.Wall

        # When player touches a wall we want to go to the menu to add the score
        collision_handler = self.space.add_collision_handler(CollisionType.Player, CollisionType.Wall)
        collision_handler.post_solve = lambda *_: self.main_menu(add_score=self.ui.score)

    def tick(self, dt: float):
        # Objects that we need to add (enemy or pellets from Level)
        to_add: List[GameObject] = []

        # Tick each object and collect new objects they may have spawned
        for obj in self.objects:
            obj.tick(dt)
            to_add.extend(obj.new_objects)
            obj.new_objects = []

        # Delete/remove dead objects
        for to_remove in [obj for obj in self.objects if obj.dead]:
            # Make sure to delete it properly (pyglets sprites need this)
            to_remove.delete()
            # Remove our tracking of the object
            self.objects.remove(to_remove)

        # Add new objects
        for obj in to_add:
            self._add_game_object(obj)

        # Run physics in overdrive to get proper segment collision at high velocity
        # If this wasn't done, the player could glitch through a wall if
        # the velocity is higher than the distance to the wall + it's depth
        for i in range(10):
            self.space.step(dt)

    def _add_game_object(self, obj: GameObject):
        """Adds an object to be internally tracked and handled

        Add an object to self.objects, make sure its event handlers are handled, and optionally add their body/shape to the physics space.
        """
        self.objects.append(obj)
        for handler in obj.event_handlers:
            self.push_handlers(handler)
        if hasattr(obj, 'body'):
            self.space.add(obj.body)
        if hasattr(obj, 'shape'):
            self.space.add(obj.shape)

    def on_draw(self):
        # First clear the canvas
        self.clear()
        # Then draw the main batch (level, enemies, pellets etc)
        self.main_batch.draw()
        # Then draw the player on top
        self.player_batch.draw()
        # Then draw the UI on top
        self.ui_batch.draw()
        # Then draw any overlay on top
        self.overlay_batch.draw()
        # And finally the FPS display
        self.fps_display.draw()


def main():
    # Create our main game window
    game_window = GameWindow(width=WIDTH, height=HEIGHT)
    # And show the main menu
    game_window.main_menu()
    # Then start the pyglet event loop
    pyglet_run()


# Call main() if file was run directly
if __name__ == "__main__":
    main()

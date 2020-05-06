from abc import ABC


class GameObject(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Flag to remove this object from the game_object list
        self.dead = False

        # List of new objects to go in the game_objects list after the tick
        self.new_objects = []

        # Tell the game handler about any event handlers
        self.event_handlers = []

    def tick(self, dt: float):
        pass

    def delete(self):
        pass

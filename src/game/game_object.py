class GameObject:
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

    def die(self):
        self.dead = True

    def delete(self):
        # Needed because Actor uses multiple inheritance and the MRO is a little funky
        # We need the hasattr since GameObject could be a non-actor that doesn't necessarily have a delete()
        if hasattr(super(), 'delete'):
            # noinspection PyUnresolvedReferences
            super().delete()

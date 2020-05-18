"""Constants needed many places in the game."""

SIZE = WIDTH, HEIGHT = (1280, 960)
TPS = 60.0


class CollisionType:
    Player = 2 ** 0
    WallKill = 2 ** 1
    WallSensor = 2 ** 2
    Pellet = 2 ** 3
    EnemyPawn = 2 ** 4
    EnemySlider = 2 ** 5

import random
from typing import Optional

from pymunk.vec2d import Vec2d
import pymunk
import pytweening

from . import Actor, resources, CollisionType, WIDTH, HEIGHT


class Enemy(Actor):
    START_SIZE = Vec2d(0, 0)

    def __init__(self, *, mass, size, img, pos, player, collision_type, batch=None, **kwargs):
        body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
        shape = pymunk.Poly.create_box(body, size, 1)
        shape.collision_type = collision_type
        super().__init__(body=body, shape=shape, img=img, batch=batch, pos=pos, **kwargs)
        self.player = player
        self.size = Vec2d(size)

        self.event_handlers = []


class EnemyPawn(Enemy):
    START_SIZE = Vec2d(32, 32)

    def __init__(self, *, pos, player, batch=None, **kwargs):
        super().__init__(mass=10, size=self.START_SIZE, img=resources.enemy_pawn_image, pos=pos, player=player,
                         batch=batch, **kwargs)
        self.speed = 10

    def tick(self, dt: float):
        super().tick(dt)

        vel = Vec2d(self.player.position) - Vec2d(self.position)
        self.body.velocity = vel.normalized() * self.speed

    @staticmethod
    def init_collision(game_window):
        collision_handler = game_window.space.add_collision_handler(CollisionType.EnemyPawn, CollisionType.Wall)
        collision_handler.begin = lambda *_: False


class EnemySlider(Enemy):
    START_SIZE = Vec2d(128, 128)

    def __init__(self, *, pos, player, batch=None, **kwargs):
        super().__init__(mass=500, size=self.START_SIZE, img=resources.enemy_slider_image, pos=pos, player=player,
                         collision_type=CollisionType.EnemySlider, batch=batch, **kwargs)

        self.speed = 100

        self.wait_timer = 0
        self.moving = False
        self.start_pos: Optional[Vec2d] = None
        self.end_pos: Optional[Vec2d] = None
        self.move_timer = 0

    @staticmethod
    def init_collision(game_window):
        def player_collision_pre_solve(arbiter, space, data):
            ps = arbiter.contact_point_set
            slider = arbiter.shapes[1].owner
            direction = (slider.end_pos - slider.start_pos).normalized()
            arbiter.shapes[0].body.position += direction * abs(ps.points[0].distance)
            # Ignore default collision response
            return False

        collision = game_window.space.add_collision_handler(CollisionType.Player, CollisionType.EnemySlider)
        collision.pre_solve = player_collision_pre_solve

        collision_handler = game_window.space.add_collision_handler(CollisionType.EnemySlider, CollisionType.Wall)
        collision_handler.begin = lambda *_: False

    def tick(self, dt: float):
        super().tick(dt)

        self.wait_timer += dt

        if not self.moving:
            if self.wait_timer > 3:
                self.moving = True
                self.move_timer = 0
            self.end_pos = Vec2d()
            self.start_pos = self.pos
            delta = self.player.pos - self.pos
            if -64 < delta.y < 64:
                self.end_pos.y = self.pos.y
                if delta.x > 0:
                    self.end_pos.x = WIDTH - self.size.x / 2
                else:
                    self.end_pos.x = self.size.x / 2
            elif -64 < delta.x < 64:
                self.end_pos.x = self.pos.x
                if delta.y > 0:
                    self.end_pos.y = HEIGHT - self.size.y / 2
                else:
                    self.end_pos.y = self.size.y / 2
            else:
                if abs(delta.x) > abs(delta.y):
                    self.end_pos.y = self.pos.y
                    self.end_pos.x = self.player.x
                else:
                    self.end_pos.x = self.pos.x
                    self.end_pos.y = self.player.y

            self.rotation = 270 - (self.start_pos - self.end_pos).angle_degrees

        if self.moving:
            self.move_timer += dt * (5 / (self.end_pos.get_distance(self.start_pos) / self.speed))
            self.body.position = self.start_pos + (self.end_pos - self.start_pos) * pytweening.easeOutBounce(
                min(self.move_timer, 1))
            if self.move_timer >= 1.0:
                self.wait_timer = 0
                self.moving = False
        else:
            self.body.velocity = (0, 0)

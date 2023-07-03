from Scripts.BaseClasses import *

import math
import time


class Bullet(Attack):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, Hitbox(4, 4), parent, dx, dy)
        self.damage = 1

    def do(self, to_x, to_y, proj_speed=5):
        length = ((to_x - self.getx()) ** 2 + (to_y - self.gety()) ** 2) ** (1 / 2)
        vector = ((to_x - self.getx()) / length * proj_speed, (to_y - self.gety()) / length * proj_speed)
        self.dx, self.dy = vector
        self.angle = math.atan2(self.dy, self.dx)
        self.sprite.image = pygame.transform.rotate(self.sprite.image, 180 - self.angle * 180 / math.pi)

    def tick(self):

        movement = ((self.x, self.y),
                    (self.x + self.dx * GameManager.time_elapsed, self.y + self.dy * GameManager.time_elapsed))

        for i in self.hitbox.check_intersections(movement):
            if i.parent == self.parent or isinstance(self.parent, Attack):
                pass
            # funny bouncing bullets
            # elif type(i.parent) == Ground:
            #     movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="bounce")
            #     self.dx *= dx_mul
            #     self.dy *= dy_mul
            elif isinstance(i.parent, Damageable):
                i.parent.hurt(self, self.damage)
                GameManager.toRemove.append(self)
            else:
                GameManager.toRemove.append(self)
        self.x = movement[1][0]
        self.y = movement[1][1]

        if not 0 < self.x < 960 or not 0 < self.y < 720:
            if self not in GameManager.toRemove:
                GameManager.toRemove.append(self)


class Bomb(Attack):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, Hitbox(4, 4), dx, dy)
        self.landed = False
        self.timer = time.time()
        self.g = 1

    def do(self, to_x, to_y):
        pass

    def tick(self):
        if not self.landed:
            self.dy += self.g * GameManager.time_elapsed
            self.y += self.dy
        for i in self.hitbox.check_intersections():
            if type(i.parent) == Ground and not self.landed:
                self.landed = True
                self.timer = time.time()
                self.hitbox.x_size = 200
                self.hitbox.y_size = 200
                self.hitbox.x -= self.hitbox.x_size
                self.hitbox.y -= self.hitbox.y_size
        if time.time() - self.timer > 2:
            GameManager.toRemove.append(self)

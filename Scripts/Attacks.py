from Scripts.BaseClasses import *
from Scripts.TestObjects import Ground
import math
import time


class Bullet(InteractableObject):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, dx, dy)
        self.hitbox = Hitbox(self, 4, 4)
        self.parent = parent
        self.damage = 1
        self.angle = 0


    def do(self, to_x, to_y):
        length = ((to_x - self.getx()) ** 2 + (to_y - self.gety()) ** 2) ** (1 / 2)
        vector = ((to_x - self.getx()) / length * 5, (to_y - self.gety()) / length * 5)
        self.dx, self.dy = vector
        self.angle = math.atan2(self.dy, self.dx)
        self.sprite.image = pygame.transform.rotate(self.sprite.image, 180-self.angle*180/math.pi)

    def tick(self):
        self.x += self.dx * GameManager.time_elapsed
        self.y += self.dy * GameManager.time_elapsed
        for i in self.hitbox.check_intersections():
            if i.parent == self.parent:
                pass
            elif i.parent != self.parent:
                GameManager.toRemove.append(self)


class CQWeapon(InteractableObject):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, dx, dy)
        self.parent = parent
        self.hitbox = Hitbox(self, self.parent.hitbox.x_size*0.75, self.parent.hitbox.y_size*0.75, 4)
        self.damage = 1
        self.angle = 0
        self.ongoing = False

    def attack(self, *args):
        if not self.ongoing:
            self.ongoing = True

    def tick(self):
        self.angle += 1
        self.x = self.parent.getx() + self.parent.hitbox.x_size - 100
        self.y = self.parent.gety()
        if self.angle == 45:
            self.angle = 0
            self.ongoing = False


class Bomb(InteractableObject):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, dx, dy)
        self.hitbox = Hitbox(self, 4, 4)
        self.parent = parent
        self.damage = 1
        self.angle = 0
        self.landed = False
        self.timer = time.time()


    def do(self, to_x, to_y):
        pass

    def tick(self):
        if not self.landed:
            self.dy += self.g * GameManager.time_elapsed
        for i in self.hitbox.check_intersections():
            if type(i.parent) == Ground:
                self.landed = True
                self.timer = time.time()
                self.hitbox = Hitbox(self, 200, 200)
                self.hitbox -= self.hitbox.x_size
                self.hitbox -= self.hitbox.y_size



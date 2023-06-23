from Scripts.BaseClasses import *
from Scripts.Attacks import Bullet, Bomb


class Gun(GameObject):
    def __init__(self, parent, x, y):
        super().__init__(x, y)
        self.parent = parent
        self.coolDown = 0

    def attack(self, x, y):
        if self.coolDown <= 0:
            self.coolDown = 150
            sprite = Sprite('Sprites/bullet1.jpg')
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            attack = Bullet(starting_x, starting_y, sprite, self.parent)
            sprite.parent = attack
            attack.do(x, y)
        else:
            self.coolDown -= GameManager.time_elapsed


class Bomber(GameObject):
    def __init__(self, parent, x, y):
        super().__init__(x, y)
        self.parent = parent
        self.coolDown = 0

    def attack(self, x, y):
        if self.coolDown <= 0:
            self.coolDown = 600
            sprite = Sprite('Sprites/bomb.png')
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            attack = Bomb(starting_x, starting_y, sprite, self.parent)
            sprite.parent = attack
            attack.do(x, y)
        else:
            self.coolDown -= GameManager.time_elapsed


class CQWeapon(InteractableObject):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        super().__init__(x, y, sprite, dx, dy)
        self.parent = parent
        self.hitbox = Hitbox(self, self.parent.hitbox.x_size*0.75, self.parent.hitbox.y_size*0.75, 4)
        self.damage = 1
        self.angle = 0
        self.ongoing = False

    def attack(self):
        if not self.ongoing:
            self.ongoing = True

    def tick(self):
        self.angle += 1
        self.x = self.parent.getx() + self.parent.hitbox.x_size - 100
        self.y = self.parent.gety()
        if self.angle == 45:
            self.angle = 0
            self.ongoing = False

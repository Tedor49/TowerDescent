from Scripts.BaseClasses import *
from Scripts.Attacks import Bullet, Bomb


class Gun(GameObject):
    def __init__(self, parent, downtime=150, proj_speed=1):
        super().__init__(0, 0)
        self.parent = parent
        self.coolDown = 0
        self.downTime = downtime
        self.projSpeed = proj_speed

    def attack(self, x, y):
        if self.coolDown <= 0:
            self.coolDown = self.downTime
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            attack = Bullet(starting_x, starting_y, Sprite('Sprites/bullet1.png'), self.parent)
            attack.do(x, y, self.projSpeed)
        else:
            self.coolDown -= GameManager.time_elapsed


class Bomber(GameObject):
    def __init__(self, parent):
        super().__init__(0, 0)
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
    def __init__(self, x, y, sprite, parent):
        self.parent = parent
        super().__init__(x, y, sprite, Hitbox(self.parent.hitbox.x_size*0.75, self.parent.hitbox.y_size*0.75, 4))
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

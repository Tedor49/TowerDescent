from Scripts.BaseClasses import *
from Scripts.Attacks import *


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


class Sword(InteractableObject):
    def __init__(self, parent, downtime=10, proj_speed=1):
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
            SwordSwing(starting_x, starting_y, x, y, self.parent)
        else:
            self.coolDown -= GameManager.time_elapsed


class Weapon(InteractableObject):
    def __init__(self, parent, attack_type, downtime=10, proj_speed=1):
        super().__init__(0, 0)
        self.parent = parent
        self.coolDown = 0
        self.attackType = attack_type
        self.downTime = downtime
        self.projSpeed = proj_speed

    def attack(self, x, y):
        if self.coolDown <= 0:
            self.coolDown = self.downTime
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            new_weapon = self.attackType(starting_x, starting_y, x, y, self.parent)()
            if new_weapon:
                self.parent.weapon.attackType = new_weapon
        else:
            self.coolDown -= GameManager.time_elapsed

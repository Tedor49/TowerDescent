from Scripts.BaseClasses import GameObject, Sprite, GameManager
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
            self.coolDown = 150
            sprite = Sprite('Sprites/bomb.jpg')
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            attack = Bomb(starting_x, starting_y, sprite, self.parent)
            sprite.parent = attack
            attack.do(x, y)
        else:
            self.coolDown -= GameManager.time_elapsed
from Scripts.BaseClasses import GameObject, Sprite, GameManager
from Scripts.Attacks import Attack


class Weapon(GameObject):
    def __init__(self, parent, x, y):
        super().__init__(x, y)
        self.parent = parent
        self.coolDown = 0

    def shoot(self, x, y):
        if self.coolDown <= 0:
            self.coolDown = 150
            sprite = Sprite('Sprites/bullet1.jpg')
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            attack = Attack(starting_x, starting_y, sprite, self.parent)
            sprite.parent = attack
            attack.do(x, y)
        else:
            self.coolDown -= GameManager.time_elapsed
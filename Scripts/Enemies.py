from Scripts.BaseClasses import *
from Scripts.Weapons import Weapon
from Scripts.Attacks import Attack


class Enemy(InteractableObject):
    def __init__(self, x, y, sprite, player_enemy, dx=0, dy=0, g=0.000):
        super().__init__(x, y, sprite, dx, dy, g)
        self.hp = 5
        self.touching_ground = False
        self.player_enemy = player_enemy


class FlyingGuy(Enemy):
    def __init__(self, x, y, sprite, player_enemy, dx=0, dy=0, g=0.000):
        super().__init__(x, y, sprite, player_enemy, dx, dy, g)
        self.weapon = Weapon(self, x, y)
        self.hitbox = Hitbox(self, 100, 100)

    def tick(self):
        if self.hp > 0:
            x = self.player_enemy.hitbox.getx() + self.player_enemy.hitbox.x_size / 2
            y = self.player_enemy.hitbox.gety() + self.player_enemy.hitbox.y_size / 2
            our_x = self.hitbox.getx() + self.hitbox.x_size / 2
            our_y = self.hitbox.gety() + self.hitbox.y_size / 2
            length = ((x - our_x) ** 2 + (y - our_y) ** 2) ** (1 / 2)
            if length < 500 and self.player_enemy.hp != 0:
                vector = ((x - our_x) / length, (y - our_y) / length)
                self.dx = vector[0] / 3
                self.dy = vector[1] / 3
                self.x += self.dx * GameManager.time_elapsed
                self.y += self.dy * GameManager.time_elapsed
                self.weapon.shoot(x, y)
                for i in self.hitbox.check_intersections():
                    if type(i.parent) == Attack and i.parent.parent != self:
                        self.hp -= 1
        else:
            GameManager.toRemove.append(self)

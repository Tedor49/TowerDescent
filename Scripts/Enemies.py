from Scripts.BaseClasses import *
from Scripts.Weapons import Gun, Bomber
from Scripts.Attacks import Bullet
from Scripts.Weapons import CQWeapon
import time


class Enemy(InteractableObject):
    def __init__(self, x, y, sprite, hitbox, player_enemy, dx=0, dy=0, g=0.000):
        super().__init__(x, y, sprite, hitbox, dx, dy, g)
        self.hp = 5
        self.player_enemy = player_enemy


class FlyingGuy(Enemy):
    def __init__(self, x, y, sprite, hitbox, player_enemy, dx=0, dy=0, g=0.000):
        super().__init__(x, y, sprite, hitbox, player_enemy, dx, dy, g)
        self.weapon = Gun(self, x, y)
        self.last_attack = time.time() - 1

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
                self.weapon.attack(x, y)
                for i in self.hitbox.check_intersections():
                    if type(i.parent) == Bullet and i.parent.parent != self and time.time() - self.last_attack > 0.6:
                        self.last_attack = time.time()
                        self.x -= 50
                        self.hp -= 1
                    if type(i.parent) == CQWeapon and i.parent.parent != self and \
                            i.parent.ongoing and time.time() - self.last_attack > 0.6:
                        self.last_attack = time.time()
                        self.x += i.parent.parent.hitbox.x_size * \
                            (self.x - i.parent.parent.getx()) / abs(self.x - i.parent.parent.getx())
                        self.hp -= 1
        else:
            GameManager.toRemove.append(self)


class SpecialFlyingGuy(Enemy):
    def __init__(self, x, y, sprite, hitbox, player_enemy, dx=0, dy=0, g=0.000):
        super().__init__(x, y, sprite, hitbox, player_enemy, dx, dy, g)
        self.weapon = Bomber(self, x, y)
        self.last_attack = time.time() - 1

    def tick(self):
        if self.hp > 0:
            x = self.player_enemy.hitbox.getx() + self.player_enemy.hitbox.x_size / 2
            y = self.player_enemy.hitbox.gety() + self.player_enemy.hitbox.y_size / 2
            our_x = self.hitbox.getx() + self.hitbox.x_size / 2
            our_y = self.hitbox.gety() + self.hitbox.y_size / 2
            length = ((x - our_x) ** 2 + (y - our_y) ** 2) ** (1 / 2)
            if length < 500 and self.player_enemy.hp != 0:
                if abs(our_x - x) < 5 and our_y < y:
                    self.weapon.attack(x, y)
                else:
                    self.x += (x - our_x) / abs(x - our_x) * GameManager.time_elapsed / 3
        else:
            GameManager.toRemove.append(self)


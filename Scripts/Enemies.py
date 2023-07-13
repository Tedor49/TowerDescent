from Scripts.BaseClasses import *
from Scripts.Weapons import *
from Scripts.Attacks import *
import time
import random


class Enemy(InteractableObject, Damageable):
    def __init__(self, x, y, sprite, hitbox, player_enemy, dx=0, dy=0, g=0.000):
        super().__init__(x, y, sprite, hitbox, dx, dy, g)
        self.player_enemy = player_enemy
        self.hitbox.ray_quality = 2


class FollowFlyingMotion(InteractableObject):
    def move(self, target):
        if target != 0:
            x = target.hitbox.getx() + target.hitbox.x_size / 2
            y = target.hitbox.gety() + target.hitbox.y_size / 2
            our_x = self.hitbox.getx() + self.hitbox.x_size / 2
            our_y = self.hitbox.gety() + self.hitbox.y_size / 2
            length = ((x - our_x) ** 2 + (y - our_y) ** 2) ** (1 / 2)
            vector = ((x - our_x) / length, (y - our_y) / length)

            self.dx += vector[0] / 900 * GameManager.time_elapsed
            self.dy += vector[1] / 900 * GameManager.time_elapsed
            self.dx *= 0.98
            self.dy *= 0.98
            self.x += self.dx * GameManager.time_elapsed
            self.y += self.dy * GameManager.time_elapsed


class FollowFlyingWallsMotion(InteractableObject):
    def move(self, target):
        if target != 0:
            x = target.hitbox.getx() + target.hitbox.x_size / 2
            y = target.hitbox.gety() + target.hitbox.y_size / 2
            our_x = self.hitbox.getx() + self.hitbox.x_size / 2
            our_y = self.hitbox.gety() + self.hitbox.y_size / 2
            length = ((x - our_x) ** 2 + (y - our_y) ** 2) ** (1 / 2)
            vector = ((x - our_x) / length, (y - our_y) / length)

            self.dx += vector[0] / 500 * GameManager.time_elapsed
            self.dy += vector[1] / 500 * GameManager.time_elapsed
            self.dx *= 0.97
            self.dy *= 0.97
            movement = [[self.x, self.y],
                        [self.x + self.dx * GameManager.time_elapsed,
                         self.y + self.dy * GameManager.time_elapsed]]

            for i in self.hitbox.check_intersections(movement):
                if type(i.parent) == Ground:
                    movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="slide")
                    self.dx *= dx_mul
                    self.dy *= dy_mul

            self.x = movement[1][0]
            self.y = movement[1][1]


def sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    return -1


class FollowWalkingMotion(InteractableObject):
    def move(self, target):
        if target != 0:
            x = target.hitbox.getx() + target.hitbox.x_size / 2
            our_x = self.hitbox.getx() + self.hitbox.x_size / 2

            self.dx += sign(x - our_x) / 500 * GameManager.time_elapsed
            self.dx *= 0.9
            self.dy += self.g * GameManager.time_elapsed
            movement = [[self.x, self.y],
                        [self.x + self.dx * GameManager.time_elapsed,
                         self.y + self.dy * GameManager.time_elapsed]]

            for i in self.hitbox.check_intersections(movement):
                if type(i.parent) == Ground:
                    movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="slide")
                    self.dx *= dx_mul
                    self.dy *= dy_mul

            self.x = movement[1][0]
            self.y = movement[1][1]


class RandomWalkingMotion(InteractableObject):
    cooldown = 2
    walkTime = 0

    def move(self, target):
        if self.cooldown < 0:
            self.cooldown = 0
            self.dx = random.choice([1, -1]) / 10
            self.walkTime = random.randint(500, 2000)
            movement = [[self.x, self.y],
                        [self.x,
                         self.y + self.dy * GameManager.time_elapsed]]
        elif self.cooldown > 0:
            self.cooldown -= GameManager.time_elapsed
            movement = [[self.x, self.y],
                        [self.x,
                         self.y + self.dy * GameManager.time_elapsed]]
        else:
            self.dy += self.g * GameManager.time_elapsed
            movement = [[self.x, self.y],
                        [self.x + self.dx * GameManager.time_elapsed,
                         self.y + self.dy * GameManager.time_elapsed]]

            self.walkTime -= GameManager.time_elapsed
            if self.walkTime < 0:
                self.cooldown = random.randint(1000, 3000)

        for i in self.hitbox.check_intersections(movement):
            if type(i.parent) == Ground:
                movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="slide")
                self.dx *= dx_mul
                self.dy *= dy_mul

        self.x = movement[1][0]
        self.y = movement[1][1]


class FlyingGuy(Enemy, RandomWalkingMotion):
    def __init__(self, x, y, sprite, hitbox, player_enemy, dx=0, dy=0, g=0.002):
        super().__init__(x, y, sprite, hitbox, player_enemy, dx, dy, g)
        self.weapon = Weapon(self, SwordSwing, AnimatedSword(), downtime=500)
        self.iframes = 0.1
        self.damage = 1

    def tick(self):
        if self.hp > 0:
            x = self.player_enemy.hitbox.getx() + self.player_enemy.hitbox.x_size / 2
            y = self.player_enemy.hitbox.gety() + self.player_enemy.hitbox.y_size / 2
            if self.weapon:
                self.weapon.attack(x, y)
            self.move(self.player_enemy)
        else:
            GameManager.counter-=1
            GameManager.toRemove.append(self)

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        self.weapon.add_to_manager()
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        GameManager.all_Objects.remove(self)
        if self.weapon:
            self.weapon.delete()
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)

import pygame.transform

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


class Movement:
    def FollowFlyingMove(self, target):
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

    def FollowFlyingWallsMove(self, target):
        if target != 0:
            x = target.hitbox.getx() + target.hitbox.x_size / 2
            y = target.hitbox.gety() + target.hitbox.y_size / 2
            our_x = self.hitbox.getx() + self.hitbox.x_size / 2
            our_y = self.hitbox.gety() + self.hitbox.y_size / 2
            length = ((x - our_x) ** 2 + (y - our_y) ** 2) ** (1 / 2)
            if length < 50:
                vector = (0, 0)
            else:
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

    def FollowWalkingMove(self, target):
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

    def RandomWalkingMove(self, target):
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

    def getRandomMovement(self):
        return random.choice([Movement.FollowFlyingMove, Movement.FollowFlyingWallsMove, Movement.FollowWalkingMove, Movement.RandomWalkingMove])


def sign(x):
    if x == 0:
        return 0
    return x/abs(x)


class BaseEnemy(Enemy):
    def __init__(self, x, y, sprite, hitbox, player_enemy, move, dx=0, dy=0, g=0.002):
        super().__init__(x, y, sprite, hitbox, player_enemy, dx, dy, g)
        self.weapon = Weapon(self, random.choice([SwordKit, GunKit]), downtime=500)
        self.iframes = 0.1
        self.damage = 1
        self.cooldown = 2000
        self.fire_time = 0
        self.wall = 0
        self.walkTime = 0
        self.movement = move
        self.attack_cooldown = GameManager.time_elapsed

    def tick(self):
        if self.hp > 0:
            x = self.player_enemy.hitbox.getx() + self.player_enemy.hitbox.x_size / 2
            y = self.player_enemy.hitbox.gety() + self.player_enemy.hitbox.y_size / 2
            if self.weapon:
                if self.cooldown > 0:
                    self.cooldown -= GameManager.time_elapsed
                elif self.cooldown < 0:
                    self.fire_time = random.randint(500, 2000)
                    self.cooldown = 0
                elif self.fire_time > 0:
                    self.weapon.attack(x, y)
                    self.fire_time -= GameManager.time_elapsed
                else:
                    self.cooldown = random.randint(500, 2000)
            self.move(self.player_enemy)
        else:
            GameManager.toRemove.append(self)
            GameManager.currentRoom.filling.remove(self)

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        if self.weapon:
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

    def move(self, target):
        return self.movement(self, target)


class Boss0(Enemy):
    def __init__(self, player_enemy, elevator):
        super().__init__(384, 260, Sprite("Sprites/boss0.png", z=4), Hitbox(200, 200, x=-4), player_enemy)
        self.iframes = 0.1
        self.baseImage = self.sprite.image.copy()
        self.damage = 1
        self.hp = 1
        self.weapon = None
        self.time = 0
        self.elevator = elevator

    def tick(self):

        self.time += GameManager.time_elapsed
        sizes = self.baseImage.get_size()
        squish_fraction = 1 - (math.e ** -(self.time / 100 % 10) + math.e ** -((10 - self.time / 100) % 10)) / 4

        self.sprite.image = pygame.transform.scale(self.baseImage, (sizes[0], int(sizes[1] * squish_fraction)))
        self.sprite.y = sizes[1] * (1 - squish_fraction)

        if self.hp <= 0:
            GameManager.toRemove.append(self)
            GameManager.currentRoom.filling.remove(self)
            self.elevator.spawn()

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        GameManager.all_Objects.remove(self)
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)


class GunArm(Enemy):
    def __init__(self, player_enemy):
        super().__init__(750, 40, Sprite("Sprites/boss0Arm.png", z=4), Hitbox(126, 57, x=-4), player_enemy)
        self.iframes = 0.1
        self.weapon = Weapon(self, GunKit, damage=10, downtime=500)

    def tick(self):
        if not self.weapon:
            self.weapon = Weapon(self, GunKit, damage=10, downtime=500)
            GameManager.toAdd.append(self.weapon)

    def add_to_manager(self):
        GameManager.all_Objects.add(self)
        if self.weapon:
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
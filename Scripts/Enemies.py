import math

import pygame.transform

from Scripts.BaseClasses import *
from Scripts.Weapons import *
from Scripts.Attacks import *
import time
import random


class Enemy(InteractableObject, Damageable):
    """Interface for the enemy"""

    def __init__(self, x, y, sprite, hitbox, player_enemy, dx=0, dy=0, g=0.000):
        """
        The initialization method for the Enemy
        :param x: coordinate on the x axis
        :param y: coordinate on the x axis
        :param sprite: Sprite which will be used by an Enemy instance
        :param hitbox: Hitbox which will be used by an Enemy instance
        :param player_enemy: player, which will be target for the enemy
        :param dx: change on the x axis
        :param dy: change on the y axis
        :param g: acceleration of gravity
        """
        super().__init__(x, y, sprite, hitbox, dx, dy, g)
        self.player_enemy = player_enemy
        if self.hitbox:
            self.hitbox.ray_quality = 2


class Movement:
    """Class that provides functions for different movements"""
    hitbox = None
    dx = None
    dy = None
    g = None
    x, y = 0, 0
    cooldown = 0
    walkTime = 0

    def follow_flying_move(self, target):
        """
        Flying movement with preference to following a target and not stopping when encountering wall
        :param target: target for movement
        """
        if target != 0:
            x = target.hitbox.get_x() + target.hitbox.x_size / 2
            y = target.hitbox.get_y() + target.hitbox.y_size / 2
            our_x = self.hitbox.get_x() + self.hitbox.x_size / 2
            our_y = self.hitbox.get_y() + self.hitbox.y_size / 2
            length = ((x - our_x) ** 2 + (y - our_y) ** 2) ** (1 / 2)
            vector = ((x - our_x) / length, (y - our_y) / length)

            self.dx += vector[0] / 900 * GameManager.time_elapsed
            self.dy += vector[1] / 900 * GameManager.time_elapsed
            self.dx *= 0.98
            self.dy *= 0.98
            self.x += self.dx * GameManager.time_elapsed
            self.y += self.dy * GameManager.time_elapsed

    def follow_flying_walls_move(self, target):
        """
        Flying movement with preference to following a target and stopping when encountering wall
        :param target: target for movement
        """
        if target != 0:
            x = target.hitbox.get_x() + target.hitbox.x_size / 2
            y = target.hitbox.get_y() + target.hitbox.y_size / 2
            our_x = self.hitbox.get_x() + self.hitbox.x_size / 2
            our_y = self.hitbox.get_y() + self.hitbox.y_size / 2
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

    def follow_walking_move(self, target):
        """
        Walking movement with preference to following a target
        :param target: target for movement
        """
        if target != 0:
            x = target.hitbox.get_x() + target.hitbox.x_size / 2
            our_x = self.hitbox.get_x() + self.hitbox.x_size / 2

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

    def random_walking_move(self, target):
        """
        Walking movement with preference to random walking
        :param target: target for movement
        """
        if self.cooldown < 0:
            self.cooldown = 0
            self.dy += self.g * GameManager.time_elapsed
            self.dx = random.choice([1, -1]) / 10
            self.walkTime = random.randint(500, 2000)
            movement = [[self.x, self.y],
                        [self.x,
                         self.y + self.dy * GameManager.time_elapsed]]
        elif self.cooldown > 0:
            self.dy += self.g * GameManager.time_elapsed
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

        for hitbox in self.hitbox.check_intersections(movement):
            if type(hitbox.parent) == Ground:
                movement, dx_mul, dy_mul = hitbox.modify_movement(movement, self.hitbox, mode="slide")
                self.dx *= dx_mul
                self.dy *= dy_mul

        self.x = movement[1][0]
        self.y = movement[1][1]

    def get_random_movement(self):
        return random.choice([Movement.follow_flying_move, Movement.follow_flying_walls_move, Movement.follow_walking_move,
                              Movement.random_walking_move])


def sign(x):
    """Function thar return -1 when number is negative, 1 when number is positive, 0 when number equals 0"""
    if x == 0:
        return 0
    return x / abs(x)


class BaseEnemy(Enemy):
    """Class that represents BaseEnemy, which can be redacted"""

    def __init__(self, x, y, sprite, hitbox, player_enemy, move, dx=0, dy=0, g=0.002, weapon=None):
        """
        The initialization method for the BaseEnemy
        :param x: coordinate on the x axis
        :param y: coordinate on the y axis
        :param sprite: Sprite which will be used
        :param hitbox: Hitbox which will be used
        :param player_enemy: player which will be the target of the enemy
        :param move: type of movement
        :param dx: change on x axis
        :param dy: change on y axis
        :param g: accelerance of gravity
        :param weapon: Weapon that will be used
        """
        super().__init__(x, y, sprite, hitbox, player_enemy, dx, dy, g)
        if weapon is None:
            self.weapon = Weapon(self, random.choice([SwordKit, GunKit]), downtime=500)
        else:
            self.weapon = weapon
        self.iframes = 0.1
        self.damage = 1
        self.cooldown = 2000
        self.fire_time = 0
        self.wall = 0
        self.walkTime = 0
        self.movement = move
        self.attack_cooldown = GameManager.time_elapsed

    def tick(self):
        """Actions which Base Enemy will do each tick"""
        if self.hp > 0:
            x = self.player_enemy.hitbox.get_x() + self.player_enemy.hitbox.x_size / 2
            y = self.player_enemy.hitbox.get_y() + self.player_enemy.hitbox.y_size / 2
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
            GameManager.to_remove.append(self)

    def add_to_manager(self):
        """Method that adds BaseEnemy instance to the GameManager"""
        GameManager.all_Objects.add(self)
        if self.weapon:
            self.weapon.add_to_manager()
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that removes BaseEnemy instance from the GameManager"""
        GameManager.all_Objects.remove(self)
        if self.weapon:
            self.weapon.delete()
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)

    def move(self, target):
        """Method that simulates movement depending on which movement was specified"""
        return self.movement(self, target)


class Boss0(Enemy):
    """Class that represents boss on the first level"""

    def __init__(self, player_enemy, elevator):
        """
        The initialization method for the Boss0
        :param player_enemy: target for a boss
        :param elevator: elevator which will be spawned after death of the boss
        """
        super().__init__(384, 260, Sprite("Sprites/boss0.png", z=4), Hitbox(200, 200, x=-4), player_enemy)
        self.iframes = 0.1
        self.baseImage = self.sprite.image.copy()
        self.damage = 1
        self.hp = 50
        self.weapon = None
        self.time = 0
        self.elevator = elevator

    def tick(self):
        """Actions which boss will do each tick"""
        self.time += GameManager.time_elapsed
        sizes = self.baseImage.get_size()
        squish_fraction = 1 - (math.e ** -(self.time / 100 % 10) + math.e ** -((10 - self.time / 100) % 10)) / 4

        self.sprite.image = pygame.transform.scale(self.baseImage, (sizes[0], int(sizes[1] * squish_fraction)))
        self.sprite.y = sizes[1] * (1 - squish_fraction)

        if self.hp <= 0:
            GameManager.to_remove.append(self)
            GameManager.current_room.filling.remove(self)
            self.elevator.spawn(340)

    def add_to_manager(self):
        """Method that adds Boss0 instance to the GameManager"""
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that removes Boss0 instance from the GameManager"""
        GameManager.all_Objects.remove(self)
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)


class GunArm(Enemy):
    """Class that represents arm which gives player weapon in the boss0 room"""

    def __init__(self, player_enemy):
        """
        The initialization method for the GunArm
        :param player_enemy:
        """
        super().__init__(750, 40, Sprite("Sprites/boss0Arm.png", z=4), Hitbox(126, 57, x=-4), player_enemy)
        self.iframes = 0.1
        self.weapon = Weapon(self, GunKit, damage=10, downtime=500)

    def tick(self):
        """Actions which boss GunArm do each tick"""
        if not self.weapon:
            self.weapon = Weapon(self, GunKit, damage=10, downtime=500)
            GameManager.to_add.append(self.weapon)

    def add_to_manager(self):
        """Method that adds GunArm instance to the GameManager"""
        GameManager.all_Objects.add(self)
        if self.weapon:
            self.weapon.add_to_manager()
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that removes GunArm instance to the GameManager"""
        GameManager.all_Objects.remove(self)
        if self.weapon:
            self.weapon.delete()
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)


class Boss1(Enemy):
    """Class that represents boss on the second level"""

    def __init__(self, player_enemy, elevator):
        """
        The initialization method for the Boss1
        :param player_enemy: target for a boss
        :param elevator: elevator which will be spawned after death of the boss
        """
        super().__init__(-200, 310, Sprite("Sprites/boss1.png", z=4), Hitbox(198, 198, x=-4), player_enemy)
        self.iframes = 0.1
        self.elevator = elevator
        self.baseImage = self.sprite.image.copy()
        self.damage = 1
        self.hp = 10
        self.movement = Movement.follow_flying_move
        self.weapon = None
        self.parent = None

    def tick(self):
        """Actions which boss will do each tick"""
        x = self.player_enemy.hitbox.get_x() + self.player_enemy.hitbox.x_size / 2
        y = self.player_enemy.hitbox.get_y() + self.player_enemy.hitbox.y_size / 2

        self_center_x = self.hitbox.get_x() + self.hitbox.x_size / 2
        self_center_y = self.hitbox.get_y() + self.hitbox.y_size / 2

        angle = math.atan2(x - self_center_x, y - self_center_y) * 180 / math.pi

        self.sprite.image = pygame.transform.rotate(self.baseImage, angle)
        self.sprite.x = 99 - self.sprite.image.get_width() // 2
        self.sprite.y = 99 - self.sprite.image.get_height() // 2

        self.move(self.player_enemy)

        if self.hp <= 0:
            GameManager.to_remove.append(self)
            GameManager.current_room.filling.remove(self)
            self.elevator.spawn(585)

        for hitbox in self.hitbox.check_intersections():
            if isinstance(hitbox.parent, Damageable):
                hitbox.parent.hurt(self, self.damage)

    def move(self, target):
        """Method that simulates movement depending on which movement was specified"""
        return self.movement(self, target)

    def add_to_manager(self):
        """Method that adds Boss1 instance to the GameManager"""
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that removes Boss1 instance from the GameManager"""
        GameManager.all_Objects.remove(self)
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)

    def hurt(self, proj, value):
        """Overwriting the Damageable method so the 2nd boss is knocked back by attacks"""

        if proj.parent != self and time.time() - self.last_attack > self.iframes:
            self.hp -= value
            if isinstance(proj, Bullet):
                vec = (proj.getdx(), proj.getdy())
            else:
                from_x = proj.parent.get_x() + proj.parent.hitbox.x_size / 2
                from_y = proj.parent.get_x() + proj.parent.hitbox.x_size / 2

                to_x = self.get_x() + self.hitbox.x_size / 2
                to_y = self.get_y() + self.hitbox.y_size / 2

                vec = (to_x - from_x, to_y, from_y)

            length = (vec[0] ** 2 + vec[1] ** 2) ** 0.5
            vec = (vec[0] / length, vec[1] / length)

            self.dx = vec[0]
            self.dy = vec[1]

            self.last_attack = time.time()


class Boss2(Enemy):
    """Class that represents boss on the third level"""

    def __init__(self, player_enemy):
        """
        The initialization method for the Boss2
        :param player_enemy: target for a boss
        :param elevator: elevator which will be spawned after death of the boss
        """
        super().__init__(400, 30, Sprite("Sprites/boss2.png", z=4), Hitbox(180, 250, x=-4), player_enemy)
        self.iframes = 0.1
        self.baseImage = self.sprite.image.copy()
        self.damage = 1
        self.hp = 20
        self.weapon = None
        self.time = 0

    def tick(self):
        """Actions which boss will do each tick"""
        self.time += GameManager.time_elapsed

        self.sprite.image = pygame.transform.rotate(self.baseImage, -math.cos(self.time / 500) * 30)
        self.x = math.sin(self.time / 500) * 360 + 480 - self.sprite.image.get_width() // 2

        if self.hp <= 0:
            GameManager.to_remove.append(self)
            GameManager.interdimensional_room.quit()
            GameManager.player.deactivate()
            GameManager.interdimensional_room = InterDimensionalRoom()
            GameManager.interdimensional_room.enter()

    def add_to_manager(self):
        """Method that adds Boss2 instance to the GameManager"""
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that removes Boss2 instance to the GameManager"""
        GameManager.all_Objects.remove(self)
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)


class Boss3(Enemy):
    """Class that represents boss on the forth level"""

    def __init__(self, player_enemy):
        """
        The initialization method for the Boss3
        :param player_enemy: target for a boss
        :param elevator: elevator which will be spawned after death of the boss
         """
        super().__init__(400, 30, Sprite("Sprites/heart.png", z=4), None, player_enemy)
        self.baseImage = self.sprite.image.copy()
        self.hp = 1
        self.weapon = None
        self.time = 0

    def tick(self):
        """Actions which boss will do each tick"""
        self.hp = GameManager.player.hp

        self.time += GameManager.time_elapsed
        size_fraction = math.sin(10 * ((self.time / 200) % 5)) * math.e ** (4 * (1 - (self.time / 200 % 5))) / 100 + 0.9
        hp_fraction = (self.hp + 100) / 200
        size_fraction *= hp_fraction * 2

        base_size = self.baseImage.get_size()
        new_size = (base_size[0] * size_fraction, base_size[1] * size_fraction)
        self.sprite.image = pygame.transform.scale(self.baseImage, new_size)

        self.x = 480 - new_size[0] // 2
        self.y = 360 - new_size[1] // 2

        brown = (139, 69, 19)

        hp_fraction = 1 - hp_fraction
        self.sprite.image.fill(tuple([255 - int((255 - i) * hp_fraction) for i in brown]),
                               special_flags=pygame.BLEND_MULT)


    def add_to_manager(self):
        """Method that adds Boss3 instance to the GameManager"""
        for elements_of_interface in GameManager.player.gui:
            elements_of_interface.active = False
        GameManager.all_Objects.add(self)
        if self.hitbox:
            GameManager.all_Hitboxes.add(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """Method that adds Boss3 instance from the GameManager"""
        for elements_of_interface in GameManager.player.gui:
            elements_of_interface.active = True
        GameManager.all_Objects.remove(self)
        if self.hitbox:
            GameManager.all_Hitboxes.remove(self.hitbox)
        if self.sprite:
            GameManager.all_Sprites.remove(self.sprite)

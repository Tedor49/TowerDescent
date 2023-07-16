from Scripts.BaseClasses import *
import math
import time


class Bullet(Attack):
    """Class that represents Bullet"""

    def __init__(self, x, y, to_x, to_y, parent, damage=1, dx=0, dy=0, proj_speed=1):
        """
        The initialization method for Bullet
        :param x: x coordinate
        :param y: y coordinate
        :param to_x: x coordinate of the direction of attack
        :param to_y: y coordinate of the direction of attack
        :param parent: Owner of this attack
        :param damage: Damage of this attack
        :param dx: change in x coordinate axis
        :param dy: change in y coordinate axis
        :param proj_speed: speed of projectile
        """
        super().__init__(x, y, Sprite('Sprites/bullet1.png'), Hitbox(4, 4), parent, dx, dy)
        self.damage = damage
        self.sprite.optimize()
        self.base_image = self.sprite.image.copy()
        length = ((to_x - self.get_x()) ** 2 + (to_y - self.get_y()) ** 2) ** (1 / 2)
        if length == 0:
            length = 0.001
        vector = ((to_x - self.get_x()) / length * proj_speed, (to_y - self.get_y()) / length * proj_speed)
        self.dx, self.dy = vector
        self.parent.weapon.sprite.play(100)

    def tick(self):
        """Method that simulates actions made by Bullet which occurs each tick"""
        from Scripts.Player import Player

        self.angle = math.atan2(self.dy, self.dx)
        self.sprite.image = pygame.transform.rotate(self.base_image, 180 - self.angle * 180 / math.pi)

        movement = ((self.x, self.y),
                    (self.x + self.dx * GameManager.time_elapsed, self.y + self.dy * GameManager.time_elapsed))

        for hitbox in self.hitbox.check_intersections(movement):
            if hitbox.parent == self.parent or isinstance(self.parent, Attack):
                continue
            elif isinstance(self.parent, Player) and isinstance(hitbox.parent,
                                                                SwordSwing) and GameManager.player.sword_reflect:
                self.parent = GameManager.player
                self.dx *= -1
                self.dy *= -1
            elif type(hitbox.parent) == Ground and isinstance(self.parent, Player) and self.parent.bullets_bounce:
                movement, dx_mul, dy_mul = hitbox.modify_movement(movement, self.hitbox, mode="bounce")
                self.dx *= dx_mul
                self.dy *= dy_mul
            elif isinstance(hitbox.parent, Damageable):
                hitbox.parent.hurt(self, self.damage)
                GameManager.to_remove.append(self)
            else:
                GameManager.to_remove.append(self)
        for i in self.hitbox.check_intersections():
            if self.parent != GameManager.player and \
                    isinstance(i.parent, SwordSwing) and \
                    GameManager.player.sword_reflect:
                self.dx *= -1
                self.dy *= -1
                self.damage *= 10
                self.parent = GameManager.player
        self.x = movement[1][0]
        self.y = movement[1][1]

        if not 0 < self.x < 960 or not 0 < self.y < 720:
            if self not in GameManager.to_remove:
                GameManager.to_remove.append(self)


class SwordSwing(Attack):
    """Class that represents SwordSwing"""

    def __init__(self, x, y, target_x, target_y, parent, damage=1, dx=0, dy=0):
        """
        The initialization method for SwordSwing
        :param x: x coordinate in relation to the position of the parent
        :param y: y coordinate in relation to the position of the parent
        :param target_x: x coordinate of the target
        :param target_y: y coordinate of the target
        :param parent: Owner of this attack
        :param damage: Damage of this attack
        :param dx: Change in x coordinate axis
        :param dy: Change in y coordinate axis
        """
        hitbox = Hitbox(parent.hitbox.x_size * 2.5, parent.hitbox.y_size * 1.75, y=-parent.hitbox.y_size * .75)
        if target_x < x:
            hitbox.x = -parent.hitbox.x_size * 1.5
        super().__init__(0, 0, None, hitbox, parent, dx, dy)
        self.timer = 300
        self.damage = damage
        self.parent.weapon.sprite.play(self.timer)

    def get_x(self):
        """
        Method that returns x coordinate of the instance
        :return: x coordinate
        """
        return self.parent.get_x() + self.x

    def get_y(self):
        """
        Method that returns y coordinate of the instance
        :return: y coordinate
        """
        return self.parent.get_y() + self.y

    def tick(self):
        """Method that simulates actions made by SwordSwing which occurs each tick"""
        self.timer -= GameManager.time_elapsed
        if self.timer < 0:
            GameManager.to_remove.append(self)

        for i in self.hitbox.check_intersections():
            if isinstance(i.parent, Damageable) and i.parent != self.parent:
                i.parent.hurt(self, self.damage)


class Fist(Attack):
    """Class that represents Fist"""

    def __init__(self, x, y, target_x, target_y, parent, damage=1, dx=0, dy=0):
        """
        The initialization method for Fist attack
        :param x: x coordinate in relation to the position of the parent
        :param y: y coordinate in relation to the position of the parent
        :param target_x: x coordinate of the target
        :param target_y: y coordinate of the target
        :param parent: Owner of this attack
        :param damage: Damage of this attack
        :param dx: Change in x coordinate axis
        :param dy: Change in y coordinate axis
        """
        hitbox = Hitbox(parent.hitbox.x_size * 2.25, parent.hitbox.y_size * .75, y=parent.hitbox.y_size * .125)
        if target_x < x:
            hitbox.x = -parent.hitbox.x_size * 1.25
        super().__init__(0, 0, None, hitbox, parent, dx, dy)
        self.timer = 100
        self.damage = damage
        self.parent.weapon.sprite.play(self.timer)

    def tick(self):
        """Method that simulates actions made by Fist which occurs each tick"""
        self.timer -= GameManager.time_elapsed
        if self.timer < 0:
            GameManager.to_remove.append(self)
        for i in self.hitbox.check_intersections():
            if isinstance(i.parent, Damageable) and i.parent != self.parent:
                i.parent.hurt(self, self.damage)
                if i.parent.weapon and not isinstance(i.parent.weapon.attack_type, Fist):
                    stolen = i.parent.weapon
                    i.parent.weapon = None
                    self.parent.change_weapon(stolen)

    def get_x(self):
        """
        Method that returns x coordinate of the instance
        :return: x coordinate
        """
        return self.parent.get_x() + self.x

    def get_y(self):
        """
        Method that returns y coordinate of the instance
        :return: y coordinate
        """
        return self.parent.get_y() + self.y

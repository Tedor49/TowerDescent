from Scripts.Attacks import *
from Scripts.AnimatedSprites import *

from typing import Type


class Gun(GameObject):
    """Class that represents Gun"""

    def __init__(self, parent, downtime=150, proj_speed=1):
        """
        The initialization method for the Gun
        :param parent: Owner of this weapon
        :param downtime: Time of the reload
        :param proj_speed: Speed of projectile of the attack
        """
        super().__init__(0, 0)
        self.parent = parent
        self.cooldown = 0
        self.downTime = downtime
        self.projectile_speed = proj_speed

    def attack(self, x, y):
        """
        Method that stimulates attack of the gun
        :param x: direction of the attack
        :param y: direction of the attack
        """
        if self.cooldown <= 0:
            self.cooldown = self.downTime
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            attack = Bullet(starting_x, starting_y, Sprite('Sprites/bullet1.png'), self.parent)
            attack.do(x, y, self.projectile_speed)
        else:
            self.cooldown -= GameManager.time_elapsed


class Sword(InteractableObject):
    """Class that represents Sword"""

    def __init__(self, parent, downtime=10, proj_speed=1):
        """
        The initialization method for the Sword
        :param parent: Owner of this weapon
        :param downtime: Time of the reload
        :param proj_speed: Speed of projectile of the attack
        """
        super().__init__(0, 0)
        self.parent = parent
        self.coolDown = 0
        self.downTime = downtime
        self.projSpeed = proj_speed

    def attack(self, x, y):
        """
        Method that stimulates attack of the sword
        :param x: direction of the attack
        :param y: direction of the attack
        """
        if self.coolDown <= 0:
            self.coolDown = self.downTime
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            SwordSwing(starting_x, starting_y, x, y, self.parent)
        else:
            self.coolDown -= GameManager.time_elapsed


class WeaponKit:
    """Class which represents collection of attribute for the weapon kit"""
    attack_type: Attack = None
    animation: Sprite = None
    gui_icon: Sprite = None
    damage: int = None


class GunKit(WeaponKit):
    """Class which represents collection of attribute for the gun kit"""
    attack_type = Bullet
    animation = AnimatedGun
    gui_icon = Sprite("Sprites/gunIcon.png")
    damage = 2


class FistKit(WeaponKit):
    """Class which represents collection of attribute for the fist kit"""
    attack_type = Fist
    animation = AnimatedFist
    gui_icon = Sprite("Sprites/fistIcon.png")
    damage = 1


class SwordKit(WeaponKit):
    """Class which represents collection of attribute for the sword kit"""
    attack_type = SwordSwing
    animation = AnimatedSword
    gui_icon = Sprite("Sprites/swordIcon.png")
    damage = 3


class Weapon(InteractableObject):
    def __init__(self, parent, weapon_kit: Type[WeaponKit], damage=-1, downtime=10, proj_speed=1):
        """
        The initialization method for the Gun
        :param parent: Owner of this weapon
        :param weapon_kit: Kit which is used
        :param damage: Damage of the weapon
        :param downtime: Time of the reload
        :param proj_speed: Speed of projectile of the attack
        """
        super().__init__(0, 0, weapon_kit.animation())
        self.parent = parent
        self.cooldown = 0
        self.attack_type = weapon_kit.attack_type
        self.gui_icon = weapon_kit.gui_icon
        self.down_time = downtime
        self.proj_speed = proj_speed
        self.ammo = -1
        self.damage = max(damage, weapon_kit.damage)

    def attack(self, x, y):
        """
        Method that stimulates attack of the weapon
        :param x: direction of the attack
        :param y: direction of the attack
        """
        if self.cooldown <= 0:
            self.ammo -= 1
            self.cooldown = self.down_time
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            self.attack_type(starting_x, starting_y, x, y, self.parent, self.damage)
            if self.ammo == 0:
                GameManager.to_remove.append(self)
                self.parent.weapon = self.parent.base
                GameManager.to_add.append(self.parent.base)
        else:
            self.cooldown -= GameManager.time_elapsed

    def add_to_manager(self):
        """ Method that adds this Weapon instance to the GameManager"""
        if isinstance(self.sprite, Sprite):
            GameManager.all_Objects.add(self.sprite)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        """ Method that removes this Weapon instance from the GameManager"""
        if isinstance(self.sprite, Sprite) and self.sprite in GameManager.all_Objects:
            GameManager.all_Objects.remove(self.sprite)
        if self.sprite and self.sprite in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self.sprite)

    def get_x(self):
        """
        Method that returns x coordinate of the weapon
        :return: x coordinate of the weapon
        """
        return self.parent.get_x() + self.x

    def get_y(self):
        """
        Method that returns y coordinate of the weapon
        :return: y coordinate of the weapon
        """
        return self.parent.get_y() + self.y

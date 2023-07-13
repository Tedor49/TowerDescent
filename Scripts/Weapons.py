import random

from Scripts.BaseClasses import *
from Scripts.Attacks import *
from Scripts.AnimatedSprites import *

from typing import Type


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


class WeaponKit:
    attack_type: Attack = None
    animation: AnimatedSprite = None
    gui_icon: Sprite = None


class GunKit(WeaponKit):
    attack_type = Bullet
    animation = AnimatedGun
    gui_icon = Sprite("Sprites/gunIcon.png")


class FistKit(WeaponKit):
    attack_type = Fist
    animation = AnimatedFist
    gui_icon = Sprite("Sprites/fistIcon.png")


class SwordKit(WeaponKit):
    attack_type = SwordSwing
    animation = AnimatedSword
    gui_icon = Sprite("Sprites/swordIcon.png")


class Weapon(InteractableObject):
    def __init__(self, parent, weapon_kit: Type[WeaponKit], downtime=10, proj_speed=1):
        super().__init__(0, 0, weapon_kit.animation())
        self.parent = parent
        self.coolDown = 0
        self.attackType = weapon_kit.attack_type
        self.guiIcon = weapon_kit.gui_icon
        self.downTime = downtime
        self.projSpeed = proj_speed
        self.ammo = -1

    def attack(self, x, y):
        if self.coolDown <= 0:
            self.ammo -= 1
            self.coolDown = self.downTime
            starting_x = self.parent.x + self.parent.hitbox.x_size / 2
            starting_y = self.parent.y + self.parent.hitbox.y_size / 2
            self.attackType(starting_x, starting_y, x, y, self.parent)
            if self.ammo == 0:
                GameManager.toRemove.append(self)
                self.parent.weapon = self.parent.base
                GameManager.toAdd.append(self.parent.base)
        else:
            self.coolDown -= GameManager.time_elapsed

    def add_to_manager(self):
        if isinstance(self.sprite, AnimatedSprite):
            GameManager.all_Objects.add(self.sprite)
        if self.sprite:
            GameManager.all_Sprites.add(self.sprite)

    def delete(self):
        if isinstance(self.sprite, AnimatedSprite) and self.sprite in GameManager.all_Objects:
            GameManager.all_Objects.remove(self.sprite)
        if self.sprite and self.sprite in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self.sprite)

    def getx(self):
        return self.parent.getx() + self.x


    def gety(self):
        return self.parent.gety() + self.y

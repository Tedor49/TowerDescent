from Scripts.BaseClasses import *
from Scripts.Attacks import *
from Scripts.Player import Player


class PowerUp(InteractableObject):
    @staticmethod
    def apply():
        pass


class DoubleJump(PowerUp):
    @staticmethod
    def apply():
        GameManager.player.max_extra_jumps += 1

class DoubleDamage(PowerUp):
    @staticmethod
    def apply():
        def change_damage_decorator(foo):
            def wrapper(self):
                foo(self)
                self.weapon.damage *= 2
            return wrapper
        Player.change_weapon = change_damage_decorator(Player.change_weapon)


class BouncingBullets(PowerUp):
    @staticmethod
    def apply():
        GameManager.player.bullets_bounce = True

class DiscardWeapon(PowerUp):
    @staticmethod
    def apply():
        def tick_decorator(foo):
            def wrapper(self):
                foo(self)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_f] and self.weapon.attackType != Fist:
                    GameManager.toRemove.append(self.weapon)
                    self.weapon = self.base
                    GameManager.toAdd.append(self.base)
            return wrapper
        Player.tick = tick_decorator(Player.tick)


class InfiniteAmmo(PowerUp):
    @staticmethod
    def apply():
        def change_ammo_decorator(foo):
            def wrapper(self):
                foo(self)
                self.weapon.ammo = -1
            return wrapper
        Player.change_weapon = change_ammo_decorator(Player.change_weapon)


class LowGravity(PowerUp):
    @staticmethod
    def apply():
        GameManager.player.g /= 4


class DecreasedCooldown(PowerUp):
    @staticmethod
    def apply():
        def change_weapon_cooldown_decorator(foo):
            def wrapper(self):
                foo(self)
                self.weapon.coolDown /= 2

            return wrapper

        Player.change_weapon = change_weapon_cooldown_decorator(Player.change_weapon)



class FistPowerUp(PowerUp):
    @staticmethod
    def apply():
        def fist_powerup_decorator(foo):
            def wrapper(self):
                pass

            return wrapper
        GameManager.player.base.damage *= 3
        GameManager.toRemove.append(GameManager.player.weapon)
        GameManager.player.weapon = GameManager.player.base
        GameManager.toAdd.append(GameManager.player.base)
        Player.change_weapon = fist_powerup_decorator(Player.change_weapon)


from Scripts.BaseClasses import *
from Scripts.Attacks import *
from Scripts.Player import Player


class PowerUp(InteractableObject):
    """Class that represents PowerUp"""

    @staticmethod
    def apply():
        """Method that applies PowerUp on the Player"""
        pass


class DoubleJump(PowerUp):
    """Class that represents DoubleJump PowerUp"""

    @staticmethod
    def apply():
        """Method that applies DoubleJump PowerUp on the Player"""
        GameManager.player.max_extra_jumps += 1


class DoubleDamage(PowerUp):
    """Class that represents DoubleDamage PowerUp"""

    @staticmethod
    def apply():
        """Method that applies DoubleDamage PowerUp on the Player"""

        def change_damage_decorator(foo):
            """
            Decorator for the changed function
            :param foo: function to be decorated
            :return: decorated function
            """

            def wrapper(self, *args):
                """
                Wrapper for PowerUp
                :param self: object itself
                :param args: arguments for the function
                """
                foo(self, *args)
                self.weapon.damage *= 2

            return wrapper

        Player.change_weapon = change_damage_decorator(Player.change_weapon)


class BouncyBullets(PowerUp):
    """Class that represents BouncyBullets PowerUp"""

    @staticmethod
    def apply():
        """Method that applies BouncyBullets PowerUp on the Player"""
        GameManager.player.bullets_bounce = True


class DiscardWeapon(PowerUp):
    """Class that represents DiscardWeapon PowerUp"""

    @staticmethod
    def apply():
        """Method that applies DiscardWeapon PowerUp on the Player"""

        def tick_decorator(foo):
            """
            Decorator for the changed function
            :param foo: function to be decorated
            :return: decorated function
            """

            def wrapper(self, *args):
                """
                Wrapper for PowerUp
                :param self: object itself
                :param args: arguments for the function
                """
                foo(self, *args)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_f] and self.weapon.attack_type != Fist:
                    GameManager.to_remove.append(self.weapon)
                    self.weapon = self.base
                    GameManager.to_add.append(self.base)

            return wrapper

        Player.tick = tick_decorator(Player.tick)


class InfiniteAmmo(PowerUp):
    """Class that represents InfiniteAmmo PowerUp"""

    @staticmethod
    def apply():
        """Method that applies InfiniteAmmo PowerUp on the Player"""

        def change_ammo_decorator(foo):
            """
            Decorator for the changed function
            :param foo: function to be decorated
            :return: decorated function
            """

            def wrapper(self, *args):
                """
                Wrapper for PowerUp
                :param self: object itself
                :param args: arguments for the function
                """
                foo(self, *args)
                self.weapon.ammo = -1

            return wrapper
        GameManager.player.weapon.ammo = -1
        Player.change_weapon = change_ammo_decorator(Player.change_weapon)


class SwordReflect(PowerUp):
    """Class that represents SwordReflect PowerUp"""

    @staticmethod
    def apply():
        """Method that applies SwordReflect PowerUp on the Player"""
        GameManager.player.sword_reflect = True


class LowGravity(PowerUp):
    """Class that represents LowGravity PowerUp"""

    @staticmethod
    def apply():
        """Method that applies LowGravity PowerUp on the Player"""
        GameManager.player.g /= 2


class LowerCooldown(PowerUp):
    """Class that represents LowerCooldown PowerUp"""

    @staticmethod
    def apply():
        """Method that applies LowerCooldown PowerUp on the Player"""

        def change_weapon_cooldown_decorator(foo):
            """
            Decorator for the changed function
            :param foo: function to be decorated
            :return: decorated function
            """

            def wrapper(self, *args):
                """
                Wrapper for PowerUp
                :param self: object itself
                :param args: arguments for the function
                """
                foo(self, *args)
                self.weapon.down_time /= 2

            return wrapper

        Player.change_weapon = change_weapon_cooldown_decorator(Player.change_weapon)


class FistPowerUp(PowerUp):
    """Class that represents FistPowerUp"""

    @staticmethod
    def apply():
        """Method that applies FistPowerUp on the Player"""

        def wrapper(self, new_weapon):
            GameManager.to_remove.append(new_weapon)

        GameManager.player.base.damage *= 3
        GameManager.player.only_fists = True
        GameManager.to_remove.append(GameManager.player.weapon)
        GameManager.player.weapon = GameManager.player.base
        GameManager.to_add.append(GameManager.player.base)
        Player.change_weapon = wrapper

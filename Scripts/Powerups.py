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


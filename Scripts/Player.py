import pygame
from Scripts.BaseClasses import GameManager, InteractableObject, Hitbox
from Scripts.Weapons import Weapon
from Scripts.TestObjects import Ground
from Scripts.Attacks import Attack
import time


class Player(InteractableObject):
    def __init__(self, x, y, sprite, dx=0, dy=0, g=0.002):
        super().__init__(x, y, sprite, dx, dy, g)
        self.hp = 1000
        self.weapon = Weapon(self, x, y)
        self.coyote = 0
        self.prev_jump_pressed = False
        self.climb_height = 7
        self.hitbox = Hitbox(self, 200, 200)
        self.last_attack = time.time() - 1

    def tick(self):
        keys = pygame.key.get_pressed()
        dx = 1
        self.x += dx * (keys[pygame.K_d] - keys[pygame.K_a]) * GameManager.time_elapsed
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.weapon.shoot(x, y)

        if keys[pygame.K_w] and not self.prev_jump_pressed and self.coyote > 0:
            self.dy = -0.5
        else:
            self.dy += self.g * GameManager.time_elapsed
        self.y += self.dy * GameManager.time_elapsed

        if keys[pygame.K_w]:
            self.prev_jump_pressed = True
        else:
            self.prev_jump_pressed = False

        self.coyote -= GameManager.time_elapsed

        for i in self.hitbox.check_intersections():
            if type(i.parent) == Attack and time.time() - self.last_attack >= 1:
                self.hp -= i.parent.damage
                self.last_attack = time.time()
                if self.hp == 0:
                    GameManager.toRemove.append(self)
            if type(i.parent) == Ground:
                climbed = 0
                while self.hitbox.intersects(i):
                    self.y -= 0.01
                    climbed += 0.01
                    if climbed >= self.climb_height:
                        self.y += climbed
                        self.x -= dx * (keys[pygame.K_d] - keys[pygame.K_a]) * GameManager.time_elapsed
                        break
                if climbed < self.climb_height:
                    self.coyote = 100
                    self.dy = 0
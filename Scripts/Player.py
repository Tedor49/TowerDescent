import pygame
from Scripts.BaseClasses import *
from Scripts.Weapons import Weapon

class Player(InteractableObject):
    def __init__(self, x, y, sprite, dx=0, dy=0, g=0.002):
        super().__init__(x, y, sprite, dx, dy, g)
        self.weapon = Weapon(self, x, y)
        self.coyote = 0
        self.prev_jump_pressed = False
        self.climb_height = 7
        self.hitbox = Hitbox(self, 200, 200)
        self.hitbox.ray_quality = 5
        self.x_speed = 1

    def tick(self):
        #print(self.x, self.y)
        keys = pygame.key.get_pressed()

        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.weapon.shoot(x, y)

        if keys[pygame.K_w] and not self.prev_jump_pressed and self.coyote > 0:
            self.dy = -0.5
        else:
            self.dy += self.g * GameManager.time_elapsed

        if keys[pygame.K_w]:
            self.prev_jump_pressed = True
        else:
            self.prev_jump_pressed = False

        self.coyote -= GameManager.time_elapsed

        movement = [[self.x, self.y],
                    [self.x + self.x_speed * (keys[pygame.K_d] - keys[pygame.K_a]) * GameManager.time_elapsed,
                     self.y + self.dy * GameManager.time_elapsed]]

        for i in self.hitbox.check_intersections(movement):
            if type(i.parent) == Ground:
                movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="slide")
                if dy_mul == 0:
                    self.coyote = 100
                self.dx *= dx_mul
                self.dy *= dy_mul

        self.x = movement[1][0]
        self.y = movement[1][1]
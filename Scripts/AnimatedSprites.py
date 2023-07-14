import pygame.image

from Scripts.BaseClasses import *
import math


class AnimatedSprite(Sprite):
    def __init__(self, image, stretch_x=1, stretch_y=1, z=1, x=0, y=0, parent=None):
        super().__init__(image, stretch_x, stretch_y, z, x, y, parent)

    def tick(self):
        pass

    def delete(self):
        if self.parent.parent != GameManager.player:
            if self in GameManager.all_Objects:
                GameManager.all_Objects.remove(self)
            if self in GameManager.all_Sprites:
                GameManager.all_Sprites.remove(self)


class AnimatedGun(AnimatedSprite):
    def __init__(self):
        super().__init__("Sprites/gun.png", z=2)
        self.base = pygame.image.load("Sprites/gun.png")
        self.flipped = pygame.transform.flip(self.base, False, True)
        self.timer = 0

    def tick(self):
        if self.parent.parent == GameManager.player:
            x, y = pygame.mouse.get_pos()
        else:
            x, y = GameManager.player.getx(), GameManager.player.gety()
        length = ((x - self.parent.parent.getx()) ** 2 + (y - self.parent.parent.gety()) ** 2) ** (1 / 2)
        if length == 0:
            length = 0.001
        vector = ((x - self.parent.parent.getx()) / length * 30, (y - self.parent.parent.gety()) / length * 30)
        angle = math.atan2(vector[1], vector[0])
        angle = - angle * 180 / math.pi
        if abs(angle) > 90:
            self.image = pygame.transform.rotate(self.flipped, angle)
        else:
            self.image = pygame.transform.rotate(self.base, angle)
        offset_x, offset_y = self.image.get_width() // 2, self.image.get_height() // 2

        if self.timer > 0:
            self.timer -= GameManager.time_elapsed
            vector = (vector[0] * 0.75, vector[1] * 0.75)

        self.x, self.y = vector[0] - offset_x + 25, vector[1] - offset_y + 25

    def play(self, timer):
        self.timer = timer


class AnimatedFist(AnimatedSprite):
    def __init__(self):
        super().__init__("Sprites/gun.png", z=2)
        self.base = pygame.image.load("Sprites/fist.png")
        self.flipped = pygame.transform.flip(self.base, False, True)
        self.timer = 0

    def tick(self):
        x, y = pygame.mouse.get_pos()
        length = ((x - self.parent.parent.getx()) ** 2 + (y - self.parent.parent.gety()) ** 2) ** (1 / 2)
        if length == 0:
            length = 0.001
        vector = ((x - self.parent.parent.getx()) / length * 30, (y - self.parent.parent.gety()) / length * 30)
        angle = math.atan2(vector[1], vector[0])
        angle = - angle * 180 / math.pi
        if abs(angle) > 90:
            angle = -180
            x = -30
            self.image = pygame.transform.rotate(self.flipped, angle)
        else:
            angle = 0
            x = 30
            self.image = pygame.transform.rotate(self.base, angle)
        offset_x, offset_y = self.image.get_width() // 2, self.image.get_height() // 2

        if self.timer > 0:
            self.timer -= GameManager.time_elapsed
            x *= 1.5

        self.x, self.y = x - offset_x + 25, - offset_y + 25

    def play(self, timer):
        self.timer = timer


class AnimatedSword(AnimatedSprite):
    def __init__(self):
        super().__init__("Sprites/sword.png", z=2)
        self.base = pygame.image.load("Sprites/sword.png")
        self.flipped = pygame.transform.flip(self.base, True, False)
        self.timer = 0
        self.total_time = 0
        self.direction = 0

    def tick(self):
        if self.timer > 0:
            self.timer -= GameManager.time_elapsed
            done_fraction = self.timer / self.total_time
            if self.direction:
                x = 30
                angle = 112.5 * done_fraction - 22.5 * (1 - done_fraction)
            else:
                x = -30
                angle = 67.5 * done_fraction + 202.5 * (1 - done_fraction)
            x -= math.cos((180 - angle) / 180 * math.pi) * 40
            y = 10 - math.sin((180 - angle) / 180 * math.pi) * 40

        else:
            if self.parent.parent == GameManager.player:
                x, y = pygame.mouse.get_pos()
            else:
                x, y = GameManager.player.getx(), GameManager.player.gety()
            length = ((x - self.parent.parent.getx()) ** 2 + (y - self.parent.parent.gety()) ** 2) ** (1 / 2)
            if length == 0:
                length = 0.001
            vector = ((x - self.parent.parent.getx()) / length * 30, (y - self.parent.parent.gety()) / length * 30)
            angle = math.atan2(vector[1], vector[0])
            angle = - angle * 180 / math.pi
            if abs(angle) > 90:
                angle = 135
                x = -40
                y = 0
            else:
                angle = 45
                x = 40
                y = 0
        self.image = pygame.transform.rotate(self.base, angle)
        offset_x, offset_y = self.image.get_width() // 2, self.image.get_height() // 2

        self.x, self.y = x - offset_x + 25, y - offset_y + 10

    def play(self, timer):
        self.timer = timer
        self.total_time = timer
        self.direction = self.x + self.image.get_width() // 2 - 25 > 0


class AnimatedExitElevator(AnimatedSprite):
    def __init__(self):
        super().__init__("Sprites/elevator.png", z=-1, y=-790)
        self.timer = 0
        self.total_time = 0
        self.direction = 0
        self.target_y = -500

    def draw(self):
        if self.parent.y < self.target_y:
            self.parent.usable = False
            self.parent.y += GameManager.time_elapsed
        elif self.parent.y > 740:
            GameManager.newLevel()
        elif self.parent.y > 0:
            self.parent.y = self.target_y
            self.parent.usable = True
        super().draw()

    def play(self, target_y):
        self.target_y = target_y


class AnimatedEntryElevator(AnimatedSprite):
    def __init__(self):
        super().__init__("Sprites/elevator.png", z=-1, y=-790 - 480, x=455)
        self.timer = 0
        self.total_time = 0
        self.direction = 0
        self.target_y = -710 + 390 - 60

    def draw(self):
        if self.y < self.target_y:
            self.y += GameManager.time_elapsed
        else:
            self.y = self.target_y
            GameManager.player.activate()
        super().draw()

    def getx(self):
        return self.x

    def gety(self):
        return self.y

    def delete(self):
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)
        if self in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self)

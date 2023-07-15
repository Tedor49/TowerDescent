import random

import pygame.image

from Scripts.BaseClasses import *
import math


class AnimatedSprite(Sprite):
    """Class that represents AnimatedSprite"""
    def __init__(self, image, stretch_x=1, stretch_y=1, z=1, x=0, y=0, parent=None):
        """
        The initialization method for the AnimatedSprite
        :param image: image that will be used in this Sprite
        :param stretch_x: stretch on the x axis
        :param stretch_y: stretch on the y axis
        :param z: coordinate on the z axis in relation to position of the parent
        :param x: coordinate on the x axis in relation to position of the parent
        :param y: coordinate on the y axis in relation to position of the parent
        :param parent: Object that owns this AnimatedSprite
        """
        super().__init__(image, stretch_x, stretch_y, z, x, y, parent)

    def tick(self):
        """Method that stimulates what AnimatedSprite do each tick"""
        pass

    def delete(self):
        """Method that deletes this AnimatedSprite instance from GameManager"""
        if self.parent.parent != GameManager.player:
            if self in GameManager.all_Objects:
                GameManager.all_Objects.remove(self)
            if self in GameManager.all_Sprites:
                GameManager.all_Sprites.remove(self)


class AnimatedGun(AnimatedSprite):
    """Class that represents AnimatedGun sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedGun
        """
        super().__init__("Sprites/gun.png", z=2)
        self.base = pygame.image.load("Sprites/gun.png")
        self.flipped = pygame.transform.flip(self.base, False, True)
        self.timer = 0

    def tick(self):
        """Method that stimulates what AnimatedGun do each tick"""
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
    """Class that represents AnimatedFist sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedFist
        """
        super().__init__("Sprites/gun.png", z=2)
        self.base = pygame.image.load("Sprites/fist.png")
        self.flipped = pygame.transform.flip(self.base, False, True)
        self.timer = 0

    def tick(self):
        """Method that stimulates what AnimatedFist do each tick"""
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
    """Class that represents AnimatedSword sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedSword
        """
        super().__init__("Sprites/sword.png", z=2)
        self.base = pygame.image.load("Sprites/sword.png")
        self.flipped = pygame.transform.flip(self.base, False, True)
        self.timer = 0
        self.total_time = 0
        self.direction = 0

    def tick(self):
        """Method that stimulates what AnimatedSword do each tick"""
        if self.timer > 0:
            self.timer -= GameManager.time_elapsed
            done_fraction = self.timer / self.total_time
            if self.direction:
                x = 30
                angle = 112.5 * done_fraction - 22.5 * (1 - done_fraction)
                self.image = pygame.transform.rotate(self.base, angle)
            else:
                x = -30
                angle = 67.5 * done_fraction + 202.5 * (1 - done_fraction)
                self.image = pygame.transform.rotate(self.flipped, angle)
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
                self.image = pygame.transform.rotate(self.flipped, angle)
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
    """Class that represents AnimatedExitElevator sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedExitElevator
        """
        if not GameManager.elevator_broken:
            cur_sprite = "Sprites/elevator.png"
        else:
            cur_sprite = "Sprites/elevator_broken_player.png"
        super().__init__(cur_sprite, z=-1, y=-790)
        self.timer = 0
        self.total_time = 0
        self.direction = 0
        self.target_y = -500

    def draw(self):
        """Method that draws this animated sprite"""
        if self.parent.y < self.target_y:
            self.parent.usable = False
            self.parent.y += GameManager.time_elapsed
        elif self.parent.y > 740:
            GameManager.currentRoom.quit()
            if GameManager.lvl_number == 2:
                GameManager.interDimensionalRoom = FakeInterDimensionalRoom()
            else:
                GameManager.interDimensionalRoom = InterDimensionalRoom()
            GameManager.interDimensionalRoom.enter()
        elif self.parent.y > 0:
            self.parent.y = self.target_y
            self.parent.usable = True
        super().draw()

    def play(self, target_y):
        self.target_y = target_y


class AnimatedEntryElevator(AnimatedSprite):
    """Class that represents AnimatedEntryElevator sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedEntryElevator
        """
        if not GameManager.elevator_broken:
            cur_sprite = "Sprites/elevator.png"
        else:
            cur_sprite = "Sprites/elevator_broken_player.png"
        super().__init__(cur_sprite, z=-1, y=-790 - 480, x=455)
        self.timer = 0
        self.total_time = 0
        self.direction = 0
        self.target_y = -710 + 390 - 60

    def draw(self):
        """Method that draws this animated sprite"""
        if self.y < self.target_y:
            self.y += GameManager.time_elapsed / 2
        else:
            self.y = self.target_y
            if GameManager.elevator_broken:
                self.image = pygame.image.load("Sprites/elevator_broken_no_player.png")
            GameManager.player.activate()
        super().draw()

    def getx(self):
        """Method that returns x coordinate of an object"""
        return self.x

    def gety(self):
        """Method that returns y coordinate of an object"""
        return self.y

    def delete(self):
        """Method that deletes this AnimatedEntryElevator instance from GameManager"""
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)
        if self in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self)


class AnimatedTop(AnimatedSprite):
    """Class that represents AnimatedTop sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedTop
        """
        super().__init__("Sprites/elevatorTop.png", z=2)
        self.dx = 0
        self.dy = 0
        self.playing = False
        self.cooldown = 5000

    def draw(self):
        """Method that draws this animated sprite"""
        from Scripts.Enemies import Boss2

        if self.playing:
            self.dy += GameManager.time_elapsed / 40
            self.x += self.dx * GameManager.time_elapsed / 40
            self.y += self.dy * GameManager.time_elapsed / 40
        else:
            self.cooldown -= GameManager.time_elapsed
            if self.cooldown < 0:
                InfiniteSpawner(970, 100)
                InfiniteSpawner(-70, 100)

                for i in GameManager.player.gui:
                    i.active = True
                GameManager.elevator_broken = True
                self.image = pygame.transform.rotate(self.image, 30)
                self.dx = random.randint(-5, 5)
                self.dy = -5
                self.playing = True
                GameManager.player.activate()

                GameManager.toAdd.append(Boss2(GameManager.player))
        super().draw()

    def delete(self):
        """Method that deletes this AnimatedTop instance from GameManager"""
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)
        if self in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self)


class AnimatedGameOver(Sprite):
    """Class that represents AnimatedGameOver sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedGameOver
        """
        super().__init__("Sprites/Levels/game_over_screen.png", z=10)
        self.timer = 5000
        self.total_time = 0
        self.direction = 0
        self.target_y = -710 + 390 - 60

    def draw(self):
        """Method that draws this animated sprite"""
        if self.timer > 0:
            self.timer -= GameManager.time_elapsed
            super().draw()
        else:
            for i in GameManager.all_Objects:
                GameManager.toRemove.append(i)
            GameManager.running = False

    def getx(self):
        """Method that returns x coordinate of an object"""
        return self.x

    def gety(self):
        """Method that returns y coordinate of an object"""
        return self.y

    def delete(self):
        """Method that deletes this AnimatedGameOver instance from GameManager"""
        if self in GameManager.all_Objects:
            GameManager.all_Objects.remove(self)
        if self in GameManager.all_Sprites:
            GameManager.all_Sprites.remove(self)


class AnimatedEnding(Sprite):
    """Class that represents AnimatedEnding sprite"""
    def __init__(self):
        """
        The initialization method for the AnimatedEnding
        """
        super().__init__("Sprites/golden_heart.png", z=10)
        self.optimize()
        self.baseImage = self.image.copy()
        GameManager.player.colliding = False
        GameManager.player.dy = 0.25
        self.time = 0
        for i in GameManager.player.gui:
            i.active = False

    def draw(self):
        """Method that draws this animated sprite"""
        GameManager.player.dy -= GameManager.time_elapsed / 10000

        self.time += GameManager.time_elapsed
        size_fraction = math.sin(10 * ((self.time / 200) % 5)) * math.e ** (4 * (1 - (self.time / 200 % 5))) / 100 + 0.9
        size_fraction *= 2

        base_size = self.baseImage.get_size()
        new_size = (base_size[0] * size_fraction, base_size[1] * size_fraction)
        self.image = pygame.transform.scale(self.baseImage, new_size)

        self.x = 480 - new_size[0] // 2
        self.y = 360 - new_size[1] // 2

        Sprite.draw(self)

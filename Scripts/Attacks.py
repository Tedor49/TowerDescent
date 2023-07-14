from Scripts.BaseClasses import *
import math
import time


class Bullet(Attack):
    def __init__(self, x, y, to_x, to_y, parent, damage=1, dx=0, dy=0, proj_speed=1):
        super().__init__(x, y, Sprite('Sprites/bullet1.png'), Hitbox(4, 4), parent, dx, dy)
        self.damage = damage
        length = ((to_x - self.getx()) ** 2 + (to_y - self.gety()) ** 2) ** (1 / 2)
        if length == 0:
            length = 0.001
        vector = ((to_x - self.getx()) / length * proj_speed, (to_y - self.gety()) / length * proj_speed)
        self.dx, self.dy = vector
        self.angle = math.atan2(self.dy, self.dx)
        self.sprite.image = pygame.transform.rotate(self.sprite.image, 180 - self.angle * 180 / math.pi)
        self.parent.weapon.sprite.play(100)

    def tick(self):
        from Scripts.Player import Player
        movement = ((self.x, self.y),
                    (self.x + self.dx * GameManager.time_elapsed, self.y + self.dy * GameManager.time_elapsed))

        for i in self.hitbox.check_intersections(movement):
            if i.parent == self.parent or isinstance(self.parent, Attack):
                pass
            elif isinstance(self.parent, Player):
                if isinstance(i.parent, SwordSwing) and GameManager.player.sword_reflect:
                    self.dx *= -1
                    self.dy *= -1
            elif type(i.parent) == Ground and isinstance(self.parent, Player):
                if self.parent.bullets_bounce:
                    movement, dx_mul, dy_mul = i.modify_movement(movement, self.hitbox, mode="bounce")
                    self.dx *= dx_mul
                    self.dy *= dy_mul
            elif isinstance(i.parent, Damageable):
                i.parent.hurt(self, self.damage)
                GameManager.toRemove.append(self)
            else:
                GameManager.toRemove.append(self)
        self.x = movement[1][0]
        self.y = movement[1][1]

        if not 0 < self.x < 960 or not 0 < self.y < 720:
            if self not in GameManager.toRemove:
                GameManager.toRemove.append(self)


class SwordSwing(Attack):
    def __init__(self, x, y, target_x, target_y, parent, damage=1, dx=0, dy=0):
        hitbox = Hitbox(parent.hitbox.x_size * 2.5, parent.hitbox.y_size * 1.75, y=-parent.hitbox.y_size * .75)
        if target_x < x:
            hitbox.x = -parent.hitbox.x_size * 1.5
        super().__init__(0, 0, None, hitbox, parent, dx, dy)
        self.timer = 300
        self.damage = damage
        self.parent.weapon.sprite.play(self.timer)

    def getx(self):
        return self.parent.getx() + self.x

    def gety(self):
        return self.parent.gety() + self.y

    def tick(self):
        self.timer -= GameManager.time_elapsed
        if self.timer < 0:
            GameManager.toRemove.append(self)

        for i in self.hitbox.check_intersections():
            if isinstance(i.parent, Damageable) and i.parent != self.parent:
                i.parent.hurt(self, self.damage)


class Bomb(Attack):
    def __init__(self, x, y, sprite, parent, damage=1, dx=0, dy=0):
        super().__init__(x, y, sprite, Hitbox(4, 4), dx, dy)
        self.landed = False
        self.timer = time.time()
        self.g = 1
        self.damage = damage

    def do(self, to_x, to_y):
        pass

    def tick(self):
        if not self.landed:
            self.dy += self.g * GameManager.time_elapsed
            self.y += self.dy
        for i in self.hitbox.check_intersections():
            if type(i.parent) == Ground and not self.landed:
                self.landed = True
                self.timer = time.time()
                self.hitbox.x_size = 200
                self.hitbox.y_size = 200
                self.hitbox.x -= self.hitbox.x_size
                self.hitbox.y -= self.hitbox.y_size
        if time.time() - self.timer > 2:
            GameManager.toRemove.append(self)


class Fist(Attack):
    def __init__(self, x, y, target_x, target_y, parent, damage=1, dx=0, dy=0):
        hitbox = Hitbox(parent.hitbox.x_size * 2.25, parent.hitbox.y_size * .75, y=parent.hitbox.y_size * .125)
        if target_x < x:
            hitbox.x = -parent.hitbox.x_size * 1.25
        super().__init__(0, 0, None, hitbox, parent, dx, dy)
        self.timer = 100
        self.damage = damage
        self.parent.weapon.sprite.play(self.timer)

    def tick(self):
        self.timer -= GameManager.time_elapsed
        if self.timer < 0:
            GameManager.toRemove.append(self)
        for i in self.hitbox.check_intersections():
            if isinstance(i.parent, Damageable) and i.parent != self.parent:
                i.parent.hurt(self, self.damage)
                if i.parent.weapon and not isinstance(i.parent.weapon.attackType, Fist):
                    stolen = i.parent.weapon
                    i.parent.weapon = None
                    self.parent.change_weapon(stolen)



    def getx(self):
        return self.parent.getx() + self.x

    def gety(self):
        return self.parent.gety() + self.y


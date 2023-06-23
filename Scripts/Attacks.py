from Scripts.BaseClasses import *


class Attack(InteractableObject):
    def __init__(self, x, y, sprite, parent, dx=0, dy=0):
        global count
        super().__init__(x, y, sprite, dx, dy)
        self.hitbox = Hitbox(self, 4, 4)
        self.parent = parent
        self.damage = 1

    def do(self, to_x, to_y):
        length = ((to_x - self.getx()) ** 2 + (to_y - self.gety()) ** 2) ** (1 / 2)
        vector = ((to_x - self.getx()) / length * 5, (to_y - self.gety()) / length * 5)
        self.dx, self.dy = vector

    def tick(self):
        movement = ((self.x, self.y),
                    (self.x + self.dx * GameManager.time_elapsed, self.y + self.dy * GameManager.time_elapsed))

        for i in self.hitbox.check_intersections(movement):
            # print(i.parent)
            if i.parent == self.parent:
                pass
            elif type(i.parent) == Ground:
                movement, dxmul, dymul = i.modify_movement(movement, self.hitbox, mode="slide")
                self.dx *= dxmul
                self.dy *= dymul
            else:
                GameManager.toRemove.append(self)

        self.x = movement[1][0]
        self.y = movement[1][1]


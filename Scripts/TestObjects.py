from Scripts.BaseClasses import *


class TargetObject(InteractableObject):
    def __init__(self, x, y, sprite, dx=0, dy=0, g=5):
        super().__init__(x, y, sprite, dx, dy, g)
        self.hitbox = Hitbox(self, 100, 100)


class Ground(InteractableObject):
    def __init__(self, x, y, sprite, dx=0, dy=0, g=5):
        super().__init__(x, y, sprite, dx, dy, g)
        self.hitbox = Hitbox(self, 400, 200)

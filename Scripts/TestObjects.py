from Scripts.BaseClasses import *


class TargetObject(InteractableObject):
    def __init__(self, x, y, sprite, hitbox, dx=0, dy=0, g=5):
        super().__init__(x, y, sprite, hitbox, dx, dy, g)

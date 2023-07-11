from Scripts.BaseClasses import *
from Scripts.Player import Player
from Scripts.TestObjects import TargetObject
from Scripts.Enemies import FlyingGuy

# bg
background = InteractableObject(0, 0, Sprite("Sprites/test_room.png", z=-2))

# walls
walls = [Ground(0, 0, 30, 720),
         Ground(0, 690, 960, 30),
         Ground(0, 0, 960, 30),
         Ground(930, 0, 30, 720)]


# platforms
platforms = [Ground(270, 150, 14*30, 30),
             Ground(270, 450, 14*30, 30),
             Ground(90, 300, 8*30, 30),
             Ground(90, 570, 8*30, 30),
             Ground(620, 300, 8*30, 30),
             Ground(620, 570, 8*30, 30)]

Player1 = Player(60, 100, Sprite('Sprites/playernew.png'), Hitbox(50, 50))
GameManager.player = Player1
cam = Camera()
GameManager.camera = cam

enemy = FlyingGuy(400, 100, Sprite('Sprites/playernew.png'), Hitbox(50, 50), Player1)
StartingRoom = Room([Player1, background, enemy] + walls + platforms)


GameManager(StartingRoom)

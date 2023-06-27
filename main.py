from Scripts.BaseClasses import *
from Scripts.Player import Player
from Scripts.TestObjects import TargetObject
from Scripts.Enemies import FlyingGuy, SpecialFlyingGuy

#bg
InteractableObject(0, 0, Sprite("Sprites/test_room.png", z=-1))

#walls
Ground(0, 0, 30, 720)
Ground(0, 690, 960, 30)
Ground(0, 0, 960, 30)
Ground(930, 0, 30, 720)

#platforms
Ground(270, 150, 14*30, 30)
Ground(270, 450, 14*30, 30)
Ground(90, 300, 8*30, 30)
Ground(90, 570, 8*30, 30)
Ground(620, 300, 8*30, 30)
Ground(620, 570, 8*30, 30)

Player1 = Player(60, 100, Sprite('Sprites/playernew.png'), Hitbox(50, 50))
GameManager.player = Player1
cam = Camera()
GameManager.camera = cam

targ = TargetObject(400, 0, Sprite('Sprites/target.png', 0.5, 0.5))
gr = Ground(0, 400, Sprite('Sprites/target.png', 0.5, 0.5))
enemy = FlyingGuy(400, 100, Sprite('Sprites/player.png', 0.5, 0.5), Player1)
StartingRoom = Room([Player1, targ, gr])
targ2 = TargetObject(400, 0, Sprite('Sprites/target.png', 0.5, 0.5))
gr2 = Ground(0, 400, Sprite('Sprites/target.png', 0.5, 0.5))
enemy2 = SpecialFlyingGuy(400, 100, Sprite('Sprites/player.png', 0.5, 0.5), Player1)
Room = Room([Player1, targ2, gr2])
Door1 = Door(300, 200, Sprite('Sprites/door.jpg'), StartingRoom, Room, None)
StartingRoom.filling.append(Door1)
Door2 = Door(300, 200, Sprite('Sprites/door.jpg'), Room, StartingRoom, Door1)
Room.filling.append(Door2)
Door1.toDoor = Door2

GameManager(StartingRoom)

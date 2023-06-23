from Scripts.BaseClasses import *
from Scripts.Player import Player
from Scripts.TestObjects import TargetObject
from Scripts.Enemies import FlyingGuy, SpecialFlyingGuy

Player1 = Player(1, 100, Sprite('Sprites/player.png'))
GameManager.player = Player1
cam = Camera()
GameManager.camera = cam

targ = TargetObject(400, 0, Sprite('Sprites/target.png', 0.5, 0.5))
gr = Ground(0, 400, Sprite('Sprites/target.png', 0.5, 0.5))
# enemy = SpecialFlyingGuy(400, 100, Sprite('Sprites/player.png', 0.5, 0.5), Player1)


GameManager()

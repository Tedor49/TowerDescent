from TowerDescent.Scripts.BaseClasses import *
from TowerDescent.Scripts.Player import Player
from TowerDescent.Scripts.TestObjects import TargetObject, Ground
from TowerDescent.Scripts.Enemies import FlyingGuy

Player1 = Player(0, 100, Sprite('Sprites/player.png'))
GameManager.player = Player1
cam = Camera()
GameManager.camera = cam

targ = TargetObject(400, 0, Sprite('Sprites/target.png', 0.5, 0.5))
gr = Ground(0, 400, Sprite('Sprites/target.png', 0.5, 0.5))
enemy = FlyingGuy(400, 100, Sprite('Sprites/player.png', 0.5, 0.5), Player1)

GameManager()

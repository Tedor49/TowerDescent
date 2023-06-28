from Scripts.BaseClasses import *
from Scripts.Player import Player
from Scripts.TestObjects import TargetObject
from Scripts.Enemies import FlyingGuy, SpecialFlyingGuy

lev = LevelGenerator()
Player1 = Player(60, 100, Sprite('Sprites/playernew.png'), Hitbox(50, 50))
GameManager.player = Player1
cam = Camera()
GameManager.camera = cam
GameManager(GameManager.searchByID(0))
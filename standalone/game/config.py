import pygame as pg
import time
from random import randint
from math import *

winWidth = 1620
winHeight = 780
wallDist = winHeight * 0.05
speed_per_sec = winHeight
font = "game/fonts/Teko-Regular.ttf"
textSize = winHeight * 0.05
textDist = -(winHeight * 0.007)

ball_speed_per_sec = winWidth / 3


def is_colliding(obj1, obj1_size, obj2, obj2_size):
	return (obj1[0] + obj1_size[0] >= obj2[0] and obj1[0] <= obj2[0] + obj2_size[0]
    		and obj1[1] + obj1_size[1] >= obj2[1] and obj1[1] <= obj2[1] + obj2_size[1])

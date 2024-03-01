import time
import sys
import json
import asyncio
# import websockets

from .input_handler import *
from .config import *
from .Player import *
from .Wall import *
from .Ball import *
from .update import *
from .render import *
from .Menu import *
from .Pause import *
from .End import *
from .StartScreen import *

class Game:
	def __init__(self): #init class
		self.is_running = True
		pg.init()
		self.state = "menu"
		self.mode = "none"
		self.menu = Menu()
		self.pause = [False, Pause()]
		self.end = End() #faire des variation ? passer dans menu ?
		self.font = pg.font.Font(font, int(textSize))
		self.ai = []
		self.pressed = []

	def start(self, websocket):
		self.GameHub = websocket
		self.winSize = [winWidth, winHeight]
		self.win = pg.display.set_mode(self.winSize)
		pg.display.set_caption("PONG")
		# self.clock = pg.time.Clock()
		# self.fps = 100
		self.last = time.time()
 
 
	async def run(self): #run game loop # relaunch when modif state
		while True:
			await self.input()
			self.tick()
			self.render()
			# self.clock.tick(self.fps)
			await asyncio.sleep(0.01)
			
	async def input(self): #catch user input
		for event in pg.event.get():
			if event.type == pg.QUIT: #event click on cross
				self.quit()
			if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
				escape_handler(self)
			if event.type == pg.MOUSEBUTTONDOWN:
				self.mouseState = pg.mouse.get_pressed()
				self.mousePos = pg.mouse.get_pos()
				await mouse_handler(self)
    
		self.keyboardState = pg.key.get_pressed()

		input_handler(self)
		
	def tick(self): #calcul method
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		#await send info
		#await recv info
		# update_all with received

		update_all(self, delta)

		# pg.display.set_caption(str(self.clock.get_fps()))
		
	def render(self): #graphic update

		if self.state == "start":
			render_start(self)
		elif self.state == "end":
			render_end(self)
		elif self.state == "menu":
			render_menu(self)
		elif self.state == "custom":
			render_custom(self)
		elif self.pause[0]:
			render_pause(self)
		elif self.state == "game":
			render_game(self)

		pg.display.update() #call to update render
		
	def quit(self):
		pg.quit()
		self.is_running = False

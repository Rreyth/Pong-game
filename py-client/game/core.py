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
		self.id = 1
		self.GameRoom = False
		self.GameHub = websocket
		self.winSize = [winWidth, winHeight]
		self.win = pg.display.set_mode(self.winSize)
		pg.display.set_caption("PONG")
		self.last = time.time()
			
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

		if not self.is_running:
			return

		self.keyboardState = pg.key.get_pressed()

		input_handler(self)
		
	async def tick(self): #calcul method
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		await self.sendInputs()

		update_all(self, delta)

	async def sendInputs(self):
		if self.pressed.__len__() == 0:
			return

		msg = {'type' : 'input',
				'player' : self.id,
           		'inputs' : self.pressed}
  
		await self.GameRoom.send(json.dumps(msg))
		self.pressed = []

		
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

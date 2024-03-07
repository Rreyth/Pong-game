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
		pg.init()
		self.state = "menu"
		self.mode = "none"
		self.menu = Menu()
		self.pause = [False, Pause()]
		self.end = End() #faire des variation ? passer dans menu ?
		self.font = pg.font.Font(font, int(textSize))
		self.ai = []
		self.pressed = []
		self.max_score = 10
		self.players = False

	def start(self, websocket):
		self.online = False
		self.is_running = True
		self.id = 0
		self.GameRoom = False
		self.GameHub = websocket
		self.winSize = [winWidth, winHeight]
		self.win = pg.display.set_mode(self.winSize)
		pg.display.set_caption("PONG")
		self.last = time.time()
			
	async def input(self): #catch user input
		for event in pg.event.get():
			if event.type == pg.QUIT: #event click on cross
				await self.quit()
			if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
				await escape_handler(self)
			if event.type == pg.KEYDOWN and self.menu.buttons[5].highlight:
				await input_id(self, self.menu.buttons[5], event.key, event.unicode)
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

		if self.online:
			await self.sendInputs()

		await update_all(self, delta)

	async def sendInputs(self):
		if self.pressed.__len__() == 0:
			return

		msg = {'type' : 'input',
				'player' : self.id,
           		'inputs' : self.pressed}
  
		await self.GameRoom.send(json.dumps(msg))
		self.pressed = []

		
	def render(self): #graphic update

		if self.state == "waiting":
			render_wait(self)
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
		
	async def quit(self): #send endGame with end infos
		if self.is_running:
			if not self.online:
				await self.GameHub.send(json.dumps({'type' : 'endGame'}))#send endGame to serv with end infos
			else:
				if self.state == 'waiting':
					# await self.GameHub.send(json.dumps({'type' : 'quitGame', 'id' : self.id, 'cmd' : 'quitWait'}))
					await self.GameHub.send(json.dumps({'type' : 'quitGame', 'id' : self.id}))
				else:
					await self.GameRoom.send(json.dumps({'type' : 'quitGame', 'id' : self.id}))
		self.state = "quit"
		self.is_running = False
	
	def pygame_quit(self):
		pg.quit()

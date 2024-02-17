import time
import sys
import json
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
	def __init__(self, websocket): #init class
		self.GameHub = websocket
		pg.init()
		self.winSize = [winWidth, winHeight]
		self.win = pg.display.set_mode(self.winSize)
		self.clock = pg.time.Clock()
		self.fps = 120
		self.last = time.time()
		self.state = "menu"
		self.mode = "none"
		self.menu = Menu()
		self.pause = [False, Pause()]
		self.end = End() #faire des variation ? passer dans menu ?
		self.font = pg.font.Font(font, int(textSize))
		self.ai = []

	
	def run(self): #run game loop # relaunch when modif state
		while True:
			self.input()
			self.tick()
			self.render()
			self.clock.tick(self.fps)
			
	def input(self): #catch user input
		for event in pg.event.get():
			if event.type == pg.QUIT: #event click on cross
				self.quit()
			if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
				escape_handler(self)
			if event.type == pg.MOUSEBUTTONDOWN:
				self.mouseState = pg.mouse.get_pressed()
				self.mousePos = pg.mouse.get_pos()
				mouse_handler(self)
    
		self.keyboardState = pg.key.get_pressed()

		input_handler(self)
		
	def tick(self): #calcul method
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		update_all(self, delta)

		pg.display.set_caption(str(self.clock.get_fps()))
		
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
		sys.exit()

	async def gameMenu(self, GameHub): ##tmp ça va bouger cette merde
		#affichage + interaction des menus
		#send game info to socket
		#recv creation success waiting or join success etc... + game address
		#return game address
		msg = {"type" : "quickGame", "cmd" : "join", "mode" : "local"}
		await GameHub.send(json.dumps(msg))
		response : dict = json.loads(await GameHub.recv())
		print(response)
		#waiting screen if response = waiting
		#wait for game start msg
		#stock info
		# return gameAddress

# Game().run()
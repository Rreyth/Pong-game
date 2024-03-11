import sys
from .config import *
from .input_handler import *
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
	def __init__(self):
		pg.init()
		self.winSize = [winWidth, winHeight]
		self.win = pg.display.set_mode(self.winSize)
		self.clock = pg.time.Clock()
		self.fps = 100
		self.last = time.time()
		self.state = "menu"
		self.mode = "none"
		self.menu = Menu()
		self.pause = [False, Pause()]
		self.end = End()
		self.font = pg.font.Font(font, int(textSize))
		self.ai = []
		self.max_score = 10
		self.players = False
		self.start_screen = False

	
	def run(self):
		while True:
			self.input()
			self.tick()
			self.render()
			self.clock.tick(self.fps)
			
	def input(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.quit()
			if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
				escape_handler(self)
			if event.type == pg.MOUSEBUTTONDOWN:
				self.mouseState = pg.mouse.get_pressed()
				self.mousePos = pg.mouse.get_pos()
				mouse_handler(self)
    
		self.keyboardState = pg.key.get_pressed()

		input_handler(self)
		
	def tick(self):
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

Game().run()
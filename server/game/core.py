import time
import sys
import asyncio
import websockets
import json

from .input_handler import *
from config import *
from .Player import *
from .Wall import *
from .Ball import *
from update import *

class Game:
	def __init__(self): #init class
		self.winSize = [winWidth, winHeight]
		self.fps = 120
		self.last = time.time()
		self.state = "wait"
		self.mode = "none"
		self.clients = set()
  
		##TOUTE LES GAMES INFO #depends on mode
		self.requiered = 1
		self.ball = Ball()
		self.players = []
		self.ai = []
		self.max_score = 5
		self.walls = False
		self.obstacle = False
        ##
        
	
	async def sendAll(self, msg : dict):
		for client in self.clients:
			await client.send(json.dumps(msg))
 
	def join(self, websocket):
		self.clients.add(websocket)
		if self.clients.__len__() == self.requiered:
			self.state = 'ready'
 
	def run(self):
		while True:
			self.input()
			self.tick()
			time.sleep(0.01) # self.clock.tick(self.fps) sleep(0.01) +- 100 fps
			
	def input(self): #recv clients inputs
		pass
		# for event in pg.event.get():
		# 	if event.type == pg.QUIT: #event click on cross
		# 		self.quit()
		# 	if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
		# 		escape_handler(self)
		# 	if event.type == pg.MOUSEBUTTONDOWN:
		# 		self.mouseState = pg.mouse.get_pressed()
		# 		self.mousePos = pg.mouse.get_pos()
		# 		mouse_handler(self)
	
		# self.keyboardState = pg.key.get_pressed()

		# input_handler(self)
		
	def tick(self): #calcul method
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		update_all(self, delta)
		#send game infos
		
	def quit(self):
		sys.exit()

 
async def handle_game(websocket, path, game):
	clients.add(websocket)

	try:
		async for message in websocket:
			await parse_msg(json.loads(message), websocket, game)
			if game.state == 'ready':
				await game.sendAll({'type' : 'start'})
				# game.run()
				pass
		 
	finally:
		clients.remove(websocket)
		if clients.__len__() <= 1:
			sys.exit()


	#game hub handle
	#client handle
 
async def parse_msg(msg : dict, websocket, game):
	print(msg)
	if msg['type'] == 'create': #game creation depending on cmd
		if msg['cmd'] == 'quickGame':
			game.mode = msg['mode'] ##only up for solo
			await websocket.send(json.dumps({'type' : 'CreationSuccess'}))
	if msg['type'] == 'join':
		game.join(websocket)
	

args = sys.argv

clients = set()

async def main():
	if args.__len__() != 3:
		return
	game = Game()
	game_server = websockets.serve(lambda websocket, path: handle_game(websocket, path, game), args[1], args[2])
	await game_server
	# asyncio.create_task(send_updates())
	await asyncio.Event().wait() #task when game full run ?

if __name__ == "__main__":
	asyncio.run(main())

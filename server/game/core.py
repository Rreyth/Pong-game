import sys
import asyncio
import websockets
import json

from config import *
from Player import *
from Wall import *
from Ball import *
from update import *

class Game:
	def __init__(self): #init class
		self.winSize = [winWidth, winHeight]
		self.fps = 120
		self.last = time.time()
		self.state = "wait"
		self.mode = "none"
		self.clients = set()
		self.is_running = True
		self.start = [3, time.time()]
		self.pause = False #toujours false ? vu que on peut freeze le jeu uniquement en local game
  
		##TOUTE LES GAMES INFO #depends on mode
		self.requiered = 1
		self.ball = Ball(False)
		self.players = [Player(1, "Player1", 2, False, False), Player(2, "AI", 2, False, False)]
		self.ai = []
		self.max_score = 5
		self.walls = [Wall("up", False), Wall("down", False)]
		self.obstacle = False
		self.custom_mod = False
        ##
        
	
	async def sendAll(self, msg : dict):
		for client in self.clients:
			await client.send(json.dumps(msg))
 
	def sendUpdate(self):
		msg = {}#toutes les infos de jeu
		print("TEST SENDUPDATES")
		# self.sendAll(msg)
 
	def join(self, websocket):
		self.clients.add(websocket)
		if self.clients.__len__() == self.requiered:
			self.state = 'ready'
			
	def input(self, player_id, inputs): #recv clients inputs
		for input in inputs:
			if input == "UP":
				self.players[player_id - 1].moveUp(self.walls)
			elif input == "DOWN":
				self.players[player_id - 1].moveDown(self.walls)
			elif input == "LEFT":
				self.players[player_id - 1].moveLeft(self.walls)
			elif input == "RIGHT":
				self.players[player_id - 1].moveRight(self.walls)
			elif input == "LAUNCH" and self.ball.stick == player_id:
				self.ball.launch()

		
	def tick(self): #calcul method
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		update_all(self, delta)
		#send game infos
		
	def quit(self):
		sys.exit() #is running -> false


async def run_game():
	global game
	game.state = "start"
	while game.is_running:
		game.tick()
		game.sendUpdate()
		time.sleep(0.01)


async def handle_game(websocket, path):
	global game
	clients.add(websocket)

	try:
		async for message in websocket:
			print("jhgsfbdVdhjkfvb")
			await parse_msg(json.loads(message), websocket)
			if game.state == 'ready':
				await game.sendAll({'type' : 'start'})
				asyncio.create_task(run_game())

	# except KeyboardInterrupt:
	# 	print("CTRRLCSDACACVA")
	# 	game.is_running = False

	finally:
		print("eyhrtiubjdfn")
		game.is_running = False
		# print(websocket)
		# clients.remove(websocket)
		# if clients.__len__() <= 1:
		# 	sys.exit()

 
async def parse_msg(msg : dict, websocket):
	global game
	print(msg)
	if msg['type'] == 'create': #game creation depending on cmd
		if msg['cmd'] == 'quickGame':
			game.mode = msg['mode'] ##only up for solo
			await websocket.send(json.dumps({'type' : 'CreationSuccess'}))
	if msg['type'] == 'join':
		game.join(websocket)
	if msg['type'] == 'input' and game.state == 'game':
		game.input(msg['player'], msg['inputs'])
	

game = Game()
args = sys.argv

clients = set()

async def main():
	global game
	if args.__len__() != 3:
		return
	game_server = websockets.serve(handle_game, args[1], args[2])
	await game_server
	await asyncio.Event().wait() #useless ????

if __name__ == "__main__":
	asyncio.run(main())

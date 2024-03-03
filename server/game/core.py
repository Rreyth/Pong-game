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
		# self.fps = 120
		self.last = time.time()
		self.state = "wait"
		self.mode = "none"
		self.clients = set()
		self.is_running = True
		self.start = [4, time.time()]
		self.pause = False #toujours false ? vu que on peut freeze le jeu uniquement en local game
		self.hub = False
		self.id = 0
  
		##TOUTE LES GAMES INFO #depends on mode
		self.requiered = 2
		self.ball = Ball(False)
		self.players = [Player(1, "Player1", 2, False, False), Player(2, "Player2", 2, False, False)]
		self.ai = []
		self.max_score = 10
		self.walls = [Wall("up", False), Wall("down", False)]
		self.obstacle = False
		self.custom_mod = False
        ##
        
	
	async def sendAll(self, msg : dict):
		for client in self.clients:
			await client.send(json.dumps(msg))
 
	async def sendUpdate(self):
		if not self.is_running:
			return
		msg = {'type' : 'update',
         		'players' : [[player.paddle[0].pos.x, player.paddle[0].pos.y] for player in self.players],
		 		'ball' : [self.ball.center[0].x, self.ball.center[0].y, self.ball.stick, self.ball.speed, self.ball.dir],
     			'score' : [player.score for player in self.players]}
		await self.sendAll(msg)
 
	async def join(self, websocket):
		await self.sendAll({'type' : 'join'})
		self.clients.add(websocket)
		await websocket.send(json.dumps({'type' : 'start', 'id' : self.clients.__len__(), 'Room_id' : self.id}))
		if self.clients.__len__() == self.requiered:
			self.state = 'ready'
			await self.hub.send(json.dumps({'type' : 'Full'}))
		await websocket.send(json.dumps({'type' : 'waiting'}))

			
	def input(self, player_id, inputs):
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
		
	def quit(self):
		self.is_running = False
		# sys.exit() #is running -> false


async def run_game():
	global game
	game.state = "start"
	while game.is_running:
		game.tick()
		if not game.is_running:
			break
		await game.sendUpdate()
		if not game.is_running:
			break
		await asyncio.sleep(0.01)


async def handle_game(websocket, path):
	global clients
	global game
	clients.add(websocket)

	try:
		async for message in websocket:
			await parse_msg(json.loads(message), websocket)
			if game.state == 'ready':
				await game.sendAll({'type' : 'start'})
				asyncio.create_task(run_game())


	finally: #send end msg to gamehub (client 0)
		game.is_running = False
		# print(websocket)
		clients.remove(websocket)
		# if clients.__len__() <= 1:
		# 	return
			# sys.exit()

 
async def parse_msg(msg : dict, websocket):
	global game
	print("game", msg)
	if msg['type'] == 'create': #game creation depending on cmd
		if msg['cmd'] == 'quickGame':
			game.mode = msg['mode']
			game.id = msg['Room_id']
			await websocket.send(json.dumps({'type' : 'CreationSuccess'}))
			game.hub = websocket
	if msg['type'] == 'join':
		await game.join(websocket)
	if msg['type'] == 'input' and game.state == 'game':
		game.input(msg['player'], msg['inputs'])
	if msg['type'] == 'quitGame':
		#update les score et les wins/loses celui qui quit perd
		await game.hub.send(json.dumps({'type' : 'endGame'}))
		await game.sendAll({'type' : 'endGame'})
		game.is_running = False
		await websocket.close()
		sys.exit()
	

game = Game()
args = sys.argv

clients = set()

async def main():
	global clients
	global game
	if args.__len__() != 3:
		return
	game_server = websockets.serve(handle_game, args[1], args[2])
	# await game_server
	# await asyncio.Event().wait()

	server = await game_server
	if not game.is_running:
		server.close()
	await server.wait_closed()
	# asyncio.get_event_loop().run_until_complete(server.wait_closed())


asyncio.run(main())

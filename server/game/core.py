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
		self.last = time.time()
		self.state = "wait"
		self.clients = set()
		self.is_running = True
		self.start = [4, time.time()]
		self.hub = False
		self.id = 0
  
		self.ai = []#will move later

		self.obstacle = False
		self.custom_mod = False

    
	def initQuickGame(self):
		self.requiered = 2
		self.ball = Ball(False)
		self.players = [Player(1, "Player1", 2, False, False), Player(2, "Player2", 2, False, False)]
		self.max_score = 10
		self.walls = [Wall("up", False), Wall("down", False)]
    
	def initCustom(self, msg : dict):
		pass
    
	def endMsg(self, id):
		msg = {'type' : 'endGame'}
		if id != 0:
			for player in self.players:
				player.win = 'LOSE' if player.nb == id else 'WIN'
		msg['score'] = [player.score for player in self.players]
		msg['win'] = [player.win for player in self.players]
		return msg
 
	async def sendAll(self, msg : dict):
		for client in self.clients:
			await client.send(json.dumps(msg))
	
	async def sendHub(self, msg : dict):
		for hub in self.hub:
			await hub.send(json.dumps(msg))
 
	async def closeAll(self):
		for client in self.clients:
			await client.close()
		await self.hub.close()
 
	async def sendUpdate(self):
		if not self.is_running:
			return
		if game.state == "start":
			msg = {'type' : 'update', 'timer' : game.start[0]}
		else:
			msg = {'type' : 'update',
					'players' : [[player.paddle[0].pos.x, player.paddle[0].pos.y] for player in self.players],
					'ball' : [self.ball.center[0].x, self.ball.center[0].y, self.ball.stick, self.ball.speed, self.ball.dir],
					'score' : [player.score for player in self.players]}
			if self.obstacle:
				msg['obstacle'] = self.obstacle.solid
		await self.sendAll(msg)
 
	async def join(self, websocket):
		await self.sendAll({'type' : 'join'})
		self.clients.add(websocket)
		msg = {'type' : 'start', 'id' : self.clients.__len__(),
				'Room_id' : self.id,
				'players' : [[player.nb, player.name, player.nb_total, player.borderless, player.square] for player in game.players],
				'walls' : [[wall.pos, wall.square] for wall in game.walls],
				'ball' : game.ball.borderless}
		if self.obstacle:
			msg['obstacle'] = self.obstacle.solid
		await websocket.send(json.dumps(msg))
		if self.clients.__len__() == self.requiered:
			self.state = 'ready'
			# await self.hub.send(json.dumps({'type' : 'Full'}))
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

		
	async def tick(self): #calcul method
		tmp = time.time()
		delta = tmp - self.last
		self.last = tmp

		await update_all(self, delta)
		
	def quit(self):
		self.is_running = False
		# sys.exit() #is running -> false


async def run_game():
	global game
	game.state = "start"
	while game.is_running:
		await game.tick()
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
		# print("finally nb : ", clients.__len__())
		if clients.__len__() <= 0:
			sys.exit()

 
async def parse_msg(msg : dict, websocket):
	global game
	if msg['type'] == 'create': #game creation depending on cmd
		if game.hub:
			game.hub.add(websocket)
		else:
			game.hub = set()
			game.hub.add(websocket)	
		if msg['cmd'] == 'quickGame':
			game.id = msg['Room_id']
			game.initQuickGame()
			await websocket.send(json.dumps({'type' : 'CreationSuccess'}))
		if msg['cmd'] == 'custom':
			game.id = msg['Room_id']
			game.initCustom(msg)
			await websocket.send(json.dumps({'type' : 'CreationSuccess'}))

	if msg['type'] == 'join':
		await game.join(websocket)

	if msg['type'] == 'input' and game.state == 'game':
		game.input(msg['player'], msg['inputs'])

	if msg['type'] == 'quitGame':
		if 'cmd' in msg.keys() and msg['cmd'] == 'quitWait':
			await game.hub.send(json.dumps({'type' : 'endGame', 'cmd' : 'quitWait', 'nb' : game.clients.__len__(), 'id' : msg['id']}))
			await game.sendAll({'type' : 'endGame', 'cmd' : 'quitWait', 'id': msg['id']})
			await websocket.close()
			game.clients.remove(websocket)
			if game.clients.__len__() == 0:
				game.is_running = False
		else:
			await game.sendHub(json.dumps(game.endMsg(msg['id'])))
			# await game.hub.send(json.dumps(game.endMsg(msg['id'])))
			await game.sendAll(game.endMsg(msg['id']))
			game.is_running = False
			await websocket.close()
			# sys.exit()

	if msg['type'] == 'close':
		game.is_running = False
		await websocket.close()
		# game.state = 'quit'
		# await game.closeAll()
	

game = Game()
args = sys.argv

clients = set()

async def main():
	global clients
	global game
	if args.__len__() != 3:
		return
	game_server = websockets.serve(handle_game, args[1], args[2])
	await game_server
	await asyncio.Event().wait()

asyncio.run(main())

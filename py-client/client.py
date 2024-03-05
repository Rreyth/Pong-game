import asyncio
import websockets
import json
from game.core import *

game = Game()

async def try_connect(websocket):
	username = input("USERNAME: ")
	password = input("PASSWORD: ")

	msg = {"type" : "connect", "cmd" : "username", "username" : username, "password" : password}
	await websocket.send(json.dumps(msg))
	response : dict = json.loads(await websocket.recv())
	if response["success"] == "true":
		print("Connection success")
	else:
		print(f"Connection failed: {response['error']}")
		exit(1)


async def parse_msg(msg : dict, websocket):#todo
	global game
 
	if msg['type'] == 'join':
		game.wait_screen.nb += 1
 
	if msg['type'] == 'start':
		game.state = 'start'
		if game.id != game.players.__len__():
			game.start_screen.timer = 4

	if msg['type'] == 'update':
		for i in range(game.players.__len__()):
			game.players[i].paddle[0].pos = Vec2(pos=msg['players'][i])
			game.players[i].score = msg['score'][i]
		game.ball.center[0] = Vec2(msg['ball'][0], msg['ball'][1])
		game.ball.stick = msg['ball'][2]
		game.ball.speed = msg['ball'][3]
		game.ball.dir = msg['ball'][4]

	if msg['type'] == 'endGame':
		if 'cmd' in msg.keys() and msg['cmd'] == 'quitWait':
			if msg['id'] == game.id:
				game.state = 'menu'
				game.is_running = False
				if game.GameRoom:
					await game.GameRoom.close()
					game.GameRoom = False
			else:
				if game.id > msg['id']:
					game.id -= 1
				game.wait_screen.nb -= 1
			return
		for i in range(game.players.__len__()):
			game.players[i].score = msg['score'][i]
			game.players[i].win = msg['win'][i]
		game.is_running = False
		if game.state != 'menu' and game.state != 'quit':
			game.state = 'end'
		if game.GameRoom:
			await game.GameRoom.close()
			game.GameRoom = False

async def run_game():
	global game
	while game.is_running:
		await game.input()
		if not game.is_running:
			break
		await game.tick()
		if not game.is_running:
			break
		game.render()
		if not game.is_running:
			break
		await asyncio.sleep(0.01)


async def local_run():
	global game
	while game.is_running and not game.online:
		await game.input()
		if not game.is_running and not game.online:
			break
		await game.tick()
		game.render()
		await asyncio.sleep(0.01)


async def wait_loop():
	global game
	game.render()
	
	msg = {'type' : 'none'}
	while game.is_running and msg['type'] != 'start':
		await parse_msg(msg, game.GameHub)
		await game.input()
		if not game.is_running:
			break
		await game.tick()
		game.render()
		await asyncio.sleep(0.01)
		try:
			msg :dict = json.loads(await asyncio.wait_for(game.GameHub.recv(), timeout=0.01))
		except asyncio.TimeoutError:
			msg = {'type' : 'none'}
	if game.is_running:
		game.GameRoom = await websockets.connect(game.GameSocket)
		await game.GameRoom.send(json.dumps({'type' : 'join'}))
		msg : dict = json.loads(await game.GameRoom.recv())
		game.id = msg['id']
		game.state = 'launch'
	

async def in_game(websocket):
	global game
	game.start(websocket)
	await local_run()
	if game.is_running:
		await wait_loop()
	if game.online:
		try:
			if game.GameRoom:
				async for message in game.GameRoom:
					await parse_msg(json.loads(message), game.GameRoom) #todo #update game with received for serv
					if game.state == 'launch':
						game.state = 'waiting'
						asyncio.create_task(run_game())

		finally:
			game.is_running = False
			if game.GameRoom:
				await game.GameRoom.close()
			if game.state == 'menu' or game.state == 'end':
				await in_game(websocket)


async def main():
	global game
	async with websockets.connect("ws://localhost:6669") as websocket:
		await try_connect(websocket)
		await in_game(websocket)
		
				# else:
				# 	if game.GameHub:
				# 		#send close msg
				# 		await websocket.close() #??? maybe just break to leave the async with ??


asyncio.run(main())

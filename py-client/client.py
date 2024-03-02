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
	if msg['type'] == 'update':
		game.players[0].paddle[0].pos = Vec2(pos=msg['pos'])


async def run_menu():
	global game
	while game.state == 'menu' and game.is_running:
		await game.input()
		await game.tick()
		game.render()
		await asyncio.sleep(0.01)  
	

async def run_game():
	global game
	while game.is_running:
		await game.input()
		if not game.is_running:
			break
		await game.tick()
		game.render()
		await asyncio.sleep(0.01)


async def main():
	global game
	async with websockets.connect("ws://localhost:6669") as websocket:
		await try_connect(websocket)
		game.start(websocket)
		await run_menu()
		try:
			async for message in game.GameRoom:
				await parse_msg(json.loads(message), game.GameRoom) #todo #update game with received for serv
				if game.state == 'launch':
					game.state = 'start'
					asyncio.create_task(run_game())

		finally:
			game.is_running = False
			if game.GameRoom:
				await game.GameRoom.close()
			if game.GameHub:
				#send close msg
				await websocket.close() #??? maybe just break to leave the async with ??


asyncio.run(main())

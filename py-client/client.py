import asyncio
import websockets
import json

from game.core import *

game = Game()



	# async def game_menu(self): ##menu mode modif game_mode dict and send it to serv when click on start 
	# 	#affichage + interaction des menus
	# 	#send game info to socket
	# 	#recv creation success waiting or join success etc... + game address
	# 	#return game address
	# 	msg = {"type" : "quickGame", "cmd" : "join", "mode" : "local"}
	# 	await self.GameHub.send(json.dumps(msg))
	# 	response : dict = json.loads(await self.GameHub.recv())
	# 	print(response)
	# 	#waiting screen if response = waiting
	# 	#wait for game start msg
	# 	#stock info
	# 	# game.change la socket pour celle de la room chacal





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


  
# async def send_message(websocket): #send inputs
# 	msg = {"type" : "connect", "cmd" : "username", "username" : "test", "password" : "mabit"}
# 	print(msg)
# 	await websocket.send(json.dumps(msg))

async def receive_updates(game):
	while True:
		print(game.state)
		# if game.state == 'game':
		# 	game.players[0].paddle[0].pos.y -= 1


	# while True:
	# 	update = await websocket.recv()
	# 	print(update)


async def parse_msg(msg : dict, websocket):#todo
    print(msg)

async def run_menu(): #return le gameroom socket pour pouvoir faire un async with ??
	global game
	while game.state == 'menu' and game.is_running:
		await game.input()
		game.tick()
		game.render()
		await asyncio.sleep(0.01)  
	

async def run_game():
	global game
	while game.is_running:
		print("ASDASDAS")
		pass


async def main():
	global game
	async with websockets.connect("ws://localhost:6669") as websocket:
		await try_connect(websocket)
		game.start(websocket)
		await run_menu()
		try:
			async for message in game.GameRoom:
				await parse_msg(json.loads(message), game.GameRoom) #todo
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

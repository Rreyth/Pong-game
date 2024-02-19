import asyncio
import websockets
import json

from game.core import *




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


async def receive_updates(websocket): # receive + draw
	while True:
		update = await websocket.recv()
		print(update)
  
# async def send_message(websocket): #send inputs
# 	msg = {"type" : "connect", "cmd" : "username", "username" : "test", "password" : "mabit"}
# 	print(msg)
# 	await websocket.send(json.dumps(msg))



async def main():
	async with websockets.connect("ws://localhost:6669") as websocket:
		await try_connect(websocket)
		game = Game(websocket)
		await game.run()
		# gameAddress = await game.gameMenu() #degage chacal
  
		# await game_menu(websocket)
	
	# async with websockets.connect(game_address) as game_socket:
	# 	receive_task = asyncio.create_task(receive_updates(game_socket)) #changer le websocket pour celui de la game 
	# 	# send_task = asyncio.create_task(send_inputs(game_socket)) #send inputs
	# 	await asyncio.gather(receive_task)

asyncio.run(main())

# class Client:
# 	def __init__(self, websocket):
# 		self.GameHub = websocket
# 		self.game = Game(websocket) #give websocket ? jpense pas...... enfait si


# 	async def run(self):
# 		#self.game.run()
# 		gameAddress = await self.game.gameMenu(self.GameHub) #self.game.menu(self.GameHub) ????
  
		#async with websockets.connect(gameAddress) as gameSocket:
			#while True: ####game.run(gameSocket) ???
				#update game info with serv info
				#input
				#tick + send input to serv
				#render
				#clock
import asyncio
import websockets
import json
import os
import time
import random
import string


starting_port = 6670

class Room:
	def __init__(self, id, host, port, type, websocket):
		self.websocket = websocket
		self.id = id
		self.host = host
		self.port = port
		self.full = False
		self.type = type

rooms = {}

used_port = []
used_id = []

fordiben_port = [8000, 8001]

clients = set()

def id_generator():
	set = string.ascii_uppercase + string.digits
	id = ''.join(random.choice(set) for i in range(4))
	while id in used_id:
		id = ''.join(random.choice(set) for i in range(4))
	return id

async def connection_handler(client_msg, websocket):
	if client_msg['cmd'] == "username":
		# print(f"CONNECT, user: {client_msg['username']}, pass: {client_msg['password']}")
		#demande serv principale de verifier les creds du user
		#if success
		msg = {'type' : 'connectionRpl', 'success' : 'true', 'error' : 'none'}
		#if failure
		# msg = {'type' : 'connectionRpl', 'success' : 'false', 'error' : 'invalid username or password'}
		await websocket.send(json.dumps(msg))
	#if client_msg['cmd'] == "token":
		#same same but different
	

async def handle_quickGame(client_msg, websocket):
	global rooms, used_port, used_id
	if client_msg['cmd'] == 'quit':
		#close game room
		await websocket.send(json.dumps({'type' : 'quitWait'}))
	elif client_msg['cmd'] == 'join':
		if client_msg['online'] == 'false': #wait client to play + end game self
			await websocket.send(json.dumps({'type' : 'starting'}))
			response : dict = json.loads(await websocket.recv())
			while response['type'] != 'endGame':
				response : dict = json.loads(await websocket.recv())
			print(response)
			#send it to serv for db stockage
   

		elif client_msg['online'] == 'true':
			for room in rooms.values():
				if not room.full and room.type == 'quickGame':
					await websocket.send(json.dumps({'type' : 'GameRoom', 'ID' : room.id, 'socket' : 'ws://{}:{}'.format(room.host, room.port)}))
					try:
						async for message in room.websocket:
							if response['type'] == 'Full':
								room.full = True
							if message['type'] == 'endGame':
								used_port.remove(room.port)
								used_id.remove(room.id)
								await room.websocket.close()
								rooms.pop(room.id)
								return
					finally:
						used_port.remove(room.port)
						used_id.remove(room.id)
						rooms.pop(room.id)
						return

			port = starting_port
			while port in used_port: port = port + 2 if port + 1 in fordiben_port else port + 1
			used_port.append(port)
			host = 'localhost'
			os.system("python3 game/core.py {} {} &".format(host, port))
			time.sleep(0.1)
			async with websockets.connect("ws://{}:{}".format(host, port)) as gameSocket:
				room_id = id_generator()
				used_id.append(room_id)
				msg = {'type' : 'create', 'cmd' : 'quickGame', 'mode' : 'online', 'Room_id' : room_id}
				await gameSocket.send(json.dumps(msg))
				response : dict = json.loads(await gameSocket.recv())
				while response['type'] != 'endGame':
					print('hub', response)
					if response['type'] == 'CreationSuccess':
						rooms[room_id] = Room(room_id, host, port, 'quickGame', gameSocket)
						await websocket.send(json.dumps({'type' : 'GameRoom', 'ID' : room_id, 'socket' : 'ws://{}:{}'.format(host, port)}))

					response : dict = json.loads(await gameSocket.recv())
				await gameSocket.close()
				used_port.remove(port)
				used_id.remove(room_id)
				rooms.pop(room_id)
				#when game end close game socket
				#send it to serv for db stockage

			#create 1v1 basic room online mode


async def parse_msg(message, websocket):
	client_msg : dict = json.loads(message)

	if client_msg["type"] == "connect":
		await connection_handler(client_msg, websocket)
	if client_msg["type"] == "quickGame":
		await handle_quickGame(client_msg, websocket)
	# elif custom (plus d'info a gerer)

async def handle_client(websocket):
	clients.add(websocket)
	print(f"connected from {websocket.remote_address[0]}:{websocket.remote_address[1]}")
 
	try:
		async for message in websocket:
			# print(f"client {websocket.remote_address[1]} : {message}")
			await parse_msg(message, websocket)

	finally:
		clients.remove(websocket)
		print(f"disconnected from {websocket.remote_address[0]}:{websocket.remote_address[1]}")

# async def send_updates(): #send game room address + side / team du paddle
# 	while True:
# 		await asyncio.sleep(5)
# 		if clients:
# 			tasks = [client.send("test from serv") for client in clients]
# 			await asyncio.gather(*tasks)


async def main():
	start_server = websockets.serve(handle_client, "localhost", 6669)
	await start_server
	# asyncio.create_task(send_updates())
	await asyncio.Event().wait()

if __name__ == "__main__":
	asyncio.run(main())
 
 
 
 
 
#  os.system("commande bash") 
# Pense à rajouter & à la fin de tes commandes bash, sinon elles sont bloquantes 
# python3 manage.py shell < script.py
# -> lance le script python avec l'environment de djanfgo, donc t'as accès à la db !
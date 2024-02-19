import asyncio
import websockets
import json
import os
import time

starting_port = 6670

used_port = []

fordiben_port = [8000, 8001]

clients = set()

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
	if client_msg['cmd'] == 'quit':
		#close game room
		await websocket.send(json.dumps({'type' : 'quitWait'}))
	elif client_msg['cmd'] == 'join':
		if client_msg['mode'] == 'local':
			await websocket.send(json.dumps({'type' : 'starting'}))
			port = starting_port
			while port in used_port: port = port + 2 if port + 1 in fordiben_port else port + 1
			used_port.append(port)
			host = 'localhost'
			os.system("python3 game/core.py {} {} &".format(host, port))
			time.sleep(0.1)
			async with websockets.connect("ws://localhost:6670") as gameSocket:
				msg = {'type' : 'create', 'cmd' : 'quickGame', 'mode' : 'local'}
				await gameSocket.send(json.dumps(msg))
				response : dict = json.loads(await gameSocket.recv())
				if response['type'] == 'GameStart':
					await websocket.send(json.dumps(response))
				end_msg : dict = json.loads(await gameSocket.recv())
				while end_msg['type'] != 'endGame':
					end_msg : dict = json.loads(await gameSocket.recv())
				#transmet au serv principale les info de endGame ??

		elif client_msg['mode'] == 'solo':
			await websocket.send(json.dumps({'type' : 'starting'}))
			#create 1 vs AI room local mode
			# wait for ready msg from the game ?
		elif client_msg['mode'] == 'online':
			await websocket.send(json.dumps({'type' : 'waiting', 'RoomId' : '1234'}))#Room id gen aleat when openning the room %10000
			#create 1v1 basic room online mode
			# wait for ready msg from the game ?
		# elif custom (plus d'info a gerer)



async def parse_msg(message, websocket):
	client_msg : dict = json.loads(message)

	if client_msg["type"] == "connect":
		await connection_handler(client_msg, websocket)
	if client_msg["type"] == "quickGame":
		await handle_quickGame(client_msg, websocket)

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
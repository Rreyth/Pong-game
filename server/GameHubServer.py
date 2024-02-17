import asyncio
import websockets
import json

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
			#create 1v1 basic room local mode
			# wait for ready msg from the game ?
		else:
			await websocket.send(json.dumps({'type' : 'waiting'}))
			#create 1v1 basic room online mode
			# wait for ready msg from the game ?



async def parse_msg(message, websocket):
	client_msg : dict = json.loads(message)

	if client_msg["type"] == "connect":
		await connection_handler(client_msg, websocket)
	if client_msg["type"] == "quickGame":
		await handle_quickGame(client_msg, websocket)

async def handle_client(websocket, path):
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
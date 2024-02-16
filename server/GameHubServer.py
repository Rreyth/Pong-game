import asyncio
import websockets
import json

clients = set()

async def handle_client(websocket, path):
	clients.add(websocket)
	print(f"connected from {websocket.remote_address[0]}:{websocket.remote_address[1]}")
 
	try:
		async for message in websocket:
			print(message)

	finally:
		clients.remove(websocket)
		print(f"disconnected from {websocket.remote_address[0]}:{websocket.remote_address[1]}")

async def send_updates():
	while True:
		await asyncio.sleep(5)
		if clients:
			tasks = [client.send("test from serv") for client in clients]
			await asyncio.gather(*tasks)


async def main():
	start_server = websockets.serve(handle_client, "localhost", 6669)
	await start_server
	asyncio.create_task(send_updates())
	await asyncio.Event().wait()

if __name__ == "__main__":
	asyncio.run(main())
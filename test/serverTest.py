import asyncio
import websockets

connected_users = set()

async def handle_websocket(websocket, path):
	connected_users.add(websocket)
	try:
		async for message in websocket:
			for user in connected_users:
				await user.send(message)
	finally:
		connected_users.remove(websocket)
  
start_server = websockets.serve(handle_websocket, "localhost", 6669)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
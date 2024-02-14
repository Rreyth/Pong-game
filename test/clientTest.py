import asyncio
import websockets

async def send_message():
	async with websockets.connect('ws://localhost:6669') as websocket:
		while True:
			message = input("type here: ")
			await websocket.send(message)
			response = await websocket.recv()
			print(f"msg: {response}")
   
asyncio.run(send_message())
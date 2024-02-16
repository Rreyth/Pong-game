import asyncio
import websockets
import json


async def receive_updates(websocket):
	while True:
		update = await websocket.recv()
		print(update)
  
async def send_message(websocket):
	while True:
		await asyncio.sleep(5)
		msg = "test from cli"
		await websocket.send(msg)
  
async def main():
	async with websockets.connect("ws://localhost:6669") as websocket:
		receive_task = asyncio.create_task(receive_updates(websocket))
		send_task = asyncio.create_task(send_message(websocket))
		await asyncio.gather(receive_task, send_task)

asyncio.run(main())
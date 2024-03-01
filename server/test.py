import websockets
import time
import asyncio
import json

async def main():
	ui = await websockets.connect("ws://localhost:6670")
	await ui.send(json.dumps({'type' : 'join'}))
	print("yes")
	await asyncio.sleep(2)
	print("yes")
	await ui.close()
	print("yes")

asyncio.run(main())
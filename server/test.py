import websockets
import time
import asyncio

async def main():
	ui = await websockets.connect("ws://localhost:6670")
	time.sleep(2)
	await ui.close()

asyncio.run(main())
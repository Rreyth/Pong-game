from .config import *
from .Player import *
from .Wall import *
from .Ball import *
from .StartScreen import *
from .Pause import *
from .AI import *
from .Custom import *
from .Button import *
import websockets

class Menu:
	def __init__(self):
		self.title_font = pg.font.Font(font, int(winHeight / 3))
		self.button_size = [winWidth * 0.1, winHeight * 0.1]
		self.buttons = [Button("SOLO", (winWidth / 3) - (self.button_size[0] / 2), (winHeight / 2) - self.button_size[1], self.button_size[0], self.button_size[1], winHeight * 0.085),
                  Button("LOCAL", (winWidth / 3 * 2) - (self.button_size[0] / 2), (winHeight / 2) - self.button_size[1], self.button_size[0], self.button_size[1], winHeight * 0.085),
                  Button("ONLINE", (winWidth / 3) - (self.button_size[0] / 2), (winHeight / 3 * 2), self.button_size[0], self.button_size[1], winHeight * 0.085),
                  Button("CUSTOM", (winWidth / 3 * 2) - (self.button_size[0] / 2), (winHeight / 3 * 2), self.button_size[0], self.button_size[1], winHeight * 0.085)]

  
	def draw(self, win):
		title = self.title_font.render("PONG", True, (255, 255, 255))
		win.blit(title, ((winWidth / 2) - (title.get_size()[0] / 2), -50))
  
		for button in self.buttons:
			button.draw(win)
   
   
	async def click(self, core, mousePos):
		for button in self.buttons:
			if button.hitbox.collidepoint(mousePos):
				await setValues(button.name, core)
	
 
async def setValues(name, core):
	core.custom_mod = False
	core.obstacle = False
	if name == "LOCAL":
		msg = {"type" : "quickGame", "cmd" : "join", "online" : "false"}
		await core.GameHub.send(json.dumps(msg))
		response : dict = json.loads(await core.GameHub.recv())
  
		core.players = [Player(1, "Player1", 2, False, False), Player(2, "Player2", 2, False, False)]
		core.walls = [Wall("up", False), Wall("down", False)]
		core.ball = Ball(False)
		core.state = "start"
		core.mode = "LOCAL"
  
	if name == "SOLO":
		msg = {"type" : "quickGame", "cmd" : "join", "online" : "false"}
		await core.GameHub.send(json.dumps(msg))
		response : dict = json.loads(await core.GameHub.recv())
		# if 'socket' in response.keys():
		# 	core.GameRoom = await websockets.connect(response['socket'])
		# 	await core.GameRoom.send(json.dumps({'type' : 'join'}))
		# 	response : dict = json.loads(await core.GameRoom.recv())
		# 	if response['type'] == 'start':
		# 		core.state = "launch"
		# 		core.mode = "solo"
  
		# directly wait for game room
  
		# core.players = [Player(1, "Player1", 2, False, False), Player(2, "AI", 2, False, False)]
		# core.ai.append(AI(core.players[1]))
		# core.walls = [Wall("up", False), Wall("down", False)]
		# core.ball = Ball(False)
		# core.state = "start"
		# core.mode = "solo"
	if name == "CUSTOM":
		core.state = "custom"
		core.custom_menu = CustomMenu()
	if name == "ONLINE":
		msg = {"type" : "quickGame", "cmd" : "join", "online" : "true"}
		await core.GameHub.send(json.dumps(msg))
		response : dict = json.loads(await core.GameHub.recv())
		print(response)
		if 'socket' in response.keys():
			core.GameRoom = await websockets.connect(response['socket'])
			await core.GameRoom.send(json.dumps({'type' : 'join'}))
			response : dict = json.loads(await core.GameRoom.recv())
			if response['type'] == 'start':
				core.state = "launch"
				core.mode = "LOCAL"
  
		core.players = [Player(1, "Player1", 2, False, False), Player(2, "Player2", 2, False, False)]
		core.walls = [Wall("up", False), Wall("down", False)]
		core.ball = Ball(False)	
		core.online = True
  
		# go in waiting screen

		#waiting screen if response = waiting
		#wait for game start msg
		#stock info
	if core.mode != "none":
		core.start_screen = StartScreen(core.mode)



# async def gameMenu(self): ##tmp ça va bouger cette merde
	# 	#affichage + interaction des menus
	# 	#send game info to socket
	# 	#recv creation success waiting or join success etc... + game address
	# 	#return game address
	# 	msg = {"type" : "quickGame", "cmd" : "join", "mode" : "local"}
	# 	await self.GameHub.send(json.dumps(msg))
	# 	response : dict = json.loads(await self.GameHub.recv())
	# 	print(response)

	# 	# return gameAddress
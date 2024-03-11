from .config import *
from .Vec2 import *

def input_handler(core):
	if core.state == "game" and not core.pause[0]:
		if core.mode == "solo":
			solo_input(core)
		else:
			for player in core.players:
				if player.name == 'AI':
					ai_moves(core, player)
				else:
					player_moves(core, player)


def solo_input(core):
	if core.keyboardState[pg.K_UP] or core.keyboardState[pg.K_w]:
		core.players[0].moveUp(core.walls)
	if core.keyboardState[pg.K_DOWN] or core.keyboardState[pg.K_s]:
		core.players[0].moveDown(core.walls)
	if core.keyboardState[pg.K_SPACE] and core.ball.stick == 1:
		core.ball.launch()
	ai_moves(core, core.players[1])

def mouse_handler(core):
	if core.state == "end":
		end_input(core)
	elif core.state == "menu":
		menu_input(core)
	elif core.pause[0]:
		pause_input(core)
	elif core.state == "custom":
		custom_input(core)

def custom_input(core):
	if core.mouseState[0] and pg.mouse.get_focused():
		core.custom_menu.click(core, core.mousePos)

def end_input(core):
	if core.mouseState[0] and pg.mouse.get_focused():
		core.end.click(core, core.mousePos)

def menu_input(core):
	if core.mouseState[0] and pg.mouse.get_focused():
		core.menu.click(core, core.mousePos)

def pause_input(core):
	if core.mouseState[0] and pg.mouse.get_focused():
		core.pause[1].click(core, core.mousePos)


def ai_moves(core, player):
	for ai in core.ai:
		if ai.id == player.nb:
			for move in ai.moves:
				if move == "UP":
					player.moveUp(core.walls)
				elif move == "DOWN":
					player.moveDown(core.walls)
				elif move == "LEFT":
					player.moveLeft(core.walls)
				elif move == "RIGHT":
					player.moveRight(core.walls)
				elif move == "LAUNCH" and core.ball.stick == player.nb:
					core.ball.launch()
			ai.pos = Vec2(pos=player.paddle[0].pos)
			ai.moves = []
			break

def player_moves(core, player):
	if player.side == 'left':
		if player.nb == 1:
			if core.keyboardState[pg.K_w]:
				player.moveUp(core.walls)
			if core.keyboardState[pg.K_s]:
				player.moveDown(core.walls)
		else:
			if core.keyboardState[pg.K_t]:
				player.moveUp(core.walls)
			if core.keyboardState[pg.K_g]:
				player.moveDown(core.walls)
		if core.keyboardState[pg.K_SPACE] and core.ball.stick == player.nb:
			core.ball.launch()
	elif player.side == 'right':
		if player.nb == 2 or player.nb == 4:
			if core.keyboardState[pg.K_UP]:
				player.moveUp(core.walls)
			if core.keyboardState[pg.K_DOWN]:
				player.moveDown(core.walls)
		else:
			if core.keyboardState[pg.K_KP8]:
				player.moveUp(core.walls)
			if core.keyboardState[pg.K_KP5]:
				player.moveDown(core.walls)
		if core.keyboardState[pg.K_KP_0] and core.ball.stick == player.nb:
			core.ball.launch()
	elif player.side == 'up':
		if core.keyboardState[pg.K_t]:
			player.moveLeft(core.walls)
		if core.keyboardState[pg.K_y]:
			player.moveRight(core.walls)
		if core.keyboardState[pg.K_h] and core.ball.stick == player.nb:
			core.ball.launch()
	elif player.side == 'down':
		if core.keyboardState[pg.K_k]:
			player.moveLeft(core.walls)
		if core.keyboardState[pg.K_l]:	
			player.moveRight(core.walls)
		if core.keyboardState[pg.K_o] and core.ball.stick == player.nb:
			core.ball.launch()


def escape_handler(core):
	if core.state == "menu" or core.state == "end":
		core.quit()
	if core.state == "game":
		core.pause[0] = not core.pause[0]
		if core.pause[0]:
			core.pause[1].freeze = True
		else:
			core.pause[1].freeze = False
	if core.state == "custom":
		core.state = "menu"
		core.mode = "none"

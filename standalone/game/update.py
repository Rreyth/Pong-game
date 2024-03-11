from .config import *
from .AI import *
from .Ball import *

def update_all(core, delta):
	if core.state == "game" and not core.pause[1].freeze:

		core.ball.update(core, delta)
		if core.obstacle:
			core.obstacle.update()

		for ai in core.ai:
			ai.update(core, delta)

		for player in core.players:
			if player.score == core.max_score and core.max_score != 0:
				core.state = "end"
				player.win = "WIN"
			player.update(delta)

	if core.state == "start":
		core.start_screen.update()
		if core.start_screen.timer == 0:
			core.state = "game"

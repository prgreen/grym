from screen import Screen
from gameState import GameState
from gameStateSingleAdventure import GameStateSingleAdventure
from gameStateMultiCoop import GameStateMultiCoop

from constants import(
	GAME_MODE
)


class GameModeManager:
	""" Set game state according to game mode """

	def __init__(self, screen, playerNames, mode=GAME_MODE['SINGLE_ADVENTURE'], directory='story'):
		""" Init game state according to game mode """

		self.mode = mode
		players = [p.strip() for p in playerNames.split(',')]

		# Mode 1 player
		if self.mode == GAME_MODE['SINGLE_ADVENTURE']:
			self.gs = GameStateSingleAdventure(screen=screen, players=players[0], directory=directory)

		# Mode 2 to 4 players, 1 ball, 1 player at a time 
		elif self.mode == GAME_MODE['MULTI_COOP']:
			self.gs = GameStateMultiCoop(screen=screen, players=players)

		# Mode 2 to 4 players, 1 ball, all together 
		elif self.mode == GAME_MODE['MULTI_CLASSIC']:
			pass
		# Mode 2 to 4 players, 1 ball per player, all together 
		elif self.mode == GAME_MODE['MULTI_BALL']:
			pass



	def update(self, eventManager):
		""" Updates game state according to game mode and returns True if game over """

		gameOver, retry = self.gs.update(eventManager)

		return gameOver, retry


# TODO List
# Add arena parameter when mode different from single adventure (selected from GUI)
		
from counter import Counter
from mainBoard import MainBoard
from gameModeManager import GameModeManager
from eventManager import EventManager

from constants import *

import time
import pygame, sys
from pygame.locals import *


class Grymark:

	def __init__(self, playerNames, mode, directory):
		self.directory = directory
		self.gameWindow()
		Counter.FRAME_CNT = 0

		self.mainLoop(playerNames, mode)


	def gameWindow(self):

		pygame.init()

		# Window
		self.fpsClock = pygame.time.Clock()
		window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption(WINDOW_TITLE)
		pygame.key.set_repeat()
		self.mainBoard = MainBoard(window)
		self.evtMgr = EventManager()


	def mainLoop(self, playerNames, mode):

		retry = True

		# First game or continue
		while retry:
			# Set game mode
			gm = GameModeManager(self.mainBoard, playerNames, mode, self.directory)

			# TODO animation before beginning

			gameOver = False
			# Game loop
			while not gameOver:
				
				Counter.FRAME_CNT += 1

				# Event handling loop
				self.evtMgr.update()
				if self.evtMgr.quitEvent or self.evtMgr.escapePressed:
					pygame.quit()
					sys.exit()

				# Update game
				gameOver, retry = gm.update(self.evtMgr)

				# Update view
				gm.gs.draw()
				pygame.display.update()
				
				self.fpsClock.tick(FPS)

		#pygame.quit()
		#sys.exit()


#game = Grymark('Isoscorp, Izuviel, Protois, Kasbari', GAME_MODE['SINGLE_ADVENTURE'])
### TODO-LIST ###
# DONE - Game Over (display and ask Try Again/Quit)
# DONE - Level loading from file
# Remove dead code and use methods to match impedance
# DONE - Detecting end of level and switching levels
# Sound effects
# Improved score calculation (bonus factor for one paddle hit multiple collisions, bonus factor for long series without dying, "perfect", Trackmania-style time tiers)
# DONE - Various strengths of bricks (multiple hits to destroy)
# Special effect bricks (bonus points, fast bounce, indestructible)
# Allow N paddles M balls (in GameState and CollisionHandler)
# Falling usable objects
# Networked p2p multiplayer mode
################
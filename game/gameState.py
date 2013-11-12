from paddle import Paddle
from player import Player
from ball import Ball
from brickGrid import BrickGrid
from mainBoard import MainBoard
from screen import Screen
from collisionHandler import CollisionHandler
from counter import Counter
from soundManager import SoundManager
from counter import Counter
from visualEffectManager import VisualEffectManager
from spriteManager import SpriteManager

from constants import *

import os


class GameState(object):

	def __init__(self, screen):
		""" Init state common to all levels """
		# Init sounds
		self.sound = SoundManager(SOUND_DIR)
		self.sound.loadAllSounds()
		# Init sprites
		self.sprites = SpriteManager.getInstance(IMAGE_DIR)
		self.sprites.loadAllImages()

		self.screen = screen
		self.gameDim = self.screen.getGameDim()
		# Parse directory to get levels
		self.levels = [lvl for lvl in os.listdir(LVL_DIR) if lvl.endswith(LVL_FORMAT)]
		self.currentLvl = 0


	def initLevel(self, lvlIndex, directory=''):
		### Generate grid ###
		self.grid = BrickGrid()
		self.directory = directory
		self.grid.loadMapFromFile(LVL_DIR + self.directory + self.levels[lvlIndex])

		# Start level counter
		self.lvlTime = Counter()
		self.lvlTime.start()
		self.lvlTime.pause()

		### Concatenate objects ###
		self.objects = []
		self.objects.append(self.grid)

		self.state = STATE['NEW_LIFE']
		self.stateAfterScore = ""

		### Collision handler ###
		self.ch = CollisionHandler()


	def update(self):
		pass

	def manageGame(self, eventManager):

		""" Debug mode """
		for p in self.players:
			# Paddle move
			if eventManager.leftHeld:
				p.paddle.move(DIRECTION['X']['LEFT'], 0, eventManager.isBoostingLeft, eventManager.isBoostingRight)
			if eventManager.rightHeld:
				p.paddle.move(DIRECTION['X']['RIGHT'], 0, eventManager.isBoostingLeft, eventManager.isBoostingRight)
			if eventManager.upHeld:
				p.paddle.move(0, DIRECTION['Y']['UP'])
			if eventManager.downHeld:
				p.paddle.move(0, DIRECTION['Y']['DOWN'])
			elif not (eventManager.leftHeld or eventManager.rightHeld or eventManager.upHeld or eventManager.downHeld):
				p.paddle.idle()

		""" Release
		# Paddle move
		if eventManager.leftHeld:
			self.players[0].paddle.move(dirX=DIRECTION['X']['LEFT'], dirY=0)
		if eventManager.rightHeld:
			self.players[0].paddle.move(dirX=DIRECTION['X']['RIGHT'], dirY= 0)
		if eventManager.upHeld:
			self.players[0].paddle.move(dirX=0, dirY=DIRECTION['Y']['UP'])
		if eventManager.downHeld:
			self.players[0].paddle.move(dirX=0, dirY=DIRECTION['Y']['DOWN'])
		"""

		# Update objects
		for o in self.objects:
			o.update()

		# Update visual effects
		VisualEffectManager.getInstance().update()


	def draw(self):

		# When level in progress or beginning
		if self.state == STATE['IN_PROGRESS'] or self.state == STATE['NEW_LIFE']:
			# Draw backgrounds
			self.screen.drawAllBG(self.grid.bgColor)
			# Draw state board
			self.screen.drawStateBoard(self.grid, self.players, self.lvlTime, self.localRecord, self.worldRecord)
			# Draw game objects
			self.screen.drawObjects(self.objects)
			# Draw visual effects
			self.screen.drawVisualEffects(VisualEffectManager.getInstance().getList())

		# When level beginning or paused or life lost => print press space
		if self.state == STATE['NEW_LIFE'] or self.state == STATE['PAUSED']:
			self.screen.drawPressToContinue()
			
		# When game over or end
		if self.state == STATE['GAME_OVER'] or self.state == STATE['GAME_END']:
			# Create game over surface
			self.screen.createGameOver()
			self.screen.drawGameOver()
		else :
			# Remove game over
			self.screen.removeGameOver()
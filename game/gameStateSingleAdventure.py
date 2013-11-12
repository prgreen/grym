from paddle import Paddle
from player import Player
from ball import Ball
from brickGrid import BrickGrid
from mainBoard import MainBoard
from screen import Screen
from lib.bunch import Bunch
from collisionHandler import CollisionHandler
from gameState import GameState
from counter import Counter
from visualEffectManager import VisualEffectManager, ScoreVEF

from constants import *

import os
import random
import pygame
import lib.http as http
from math import sqrt
from pygame.constants import *

class GameStateSingleAdventure(GameState):

	def __init__(self, screen, players, directory):
		""" Init state common to all levels """
		super(GameStateSingleAdventure, self).__init__(screen)

		self.players = [Player(players)]

		# Parse directory to get levels
		self.levels = [lvl for lvl in os.listdir(LVL_DIR+directory) if lvl.endswith(LVL_FORMAT)]
		self.currentLvl = 0
		self.directory = directory+'/'
		self.initLevel(self.currentLvl, self.directory)

	def initLevel(self, lvlIndex, directory):
		""" Construct level with one ball per player """
		super(GameStateSingleAdventure, self).initLevel(self.currentLvl, directory)

		### Construct objects ###
		self.balls = []

		# Init Paddle
		posX0 = (self.gameDim[0]-PADDLE_WIDTH['INIT']) /2
		posY0 = self.gameDim[1]-3*PADDLE_HEIGHT
		self.players[0].initPaddle(padWidth=PADDLE_WIDTH['INIT'], padHeight=PADDLE_HEIGHT, padColor=self.players[0].color, padPosX0=posX0, padPosY0=posY0)

		# Ball
		posX0 = (self.gameDim[0]-10*BALL_RADIUS) /2
		posY0 = 5*self.gameDim[1]/6
		self.balls.append(Ball(radius=BALL_RADIUS, posX=posX0 , posY=posY0, color=BALL_COLOR))

		### Concatenate objects ###
		self.objects.append(self.players[0].paddle)
		self.objects.append(self.balls[0])

		# Init score chain bonus
		self.chainBonus = 0

		# Init score and boolean bonus
		self.players[0].initScore()
		self.scoreToIncrease = self.players[0].totalScore 	# Score to increase at the end of level
		self.isPerfect = True
		self.brkScore = 0									# Score generated when brick collision, to be printed
		self.isNewRecord = False
		self.lvlTrophy = None

		# Get records for the level
		self.localRecord = self.players[0].getTime(self.grid.hashsum.hexdigest())
		self.worldRecord = http.getWorldTime(self.grid.hashsum.hexdigest())
		if self.worldRecord:
			self.worldRecord = int(self.worldRecord)
		#print "LOCAL", self.localRecord
		#print "WORLD", self.worldRecord

	def update(self, eventManager):
		""" Returns True,True if game over,retry """
		super(GameStateSingleAdventure, self).update()

		# When level in progress
		if self.state == STATE['IN_PROGRESS']:
			# Unpause counters
			self.lvlTime.unpause()
			VisualEffectManager.getInstance().unpauseCounter()

			self.manageGame(eventManager)
			# Pause when player press SPACE
			if eventManager.spacePressed:
				self.state = STATE['PAUSED']

		# When game paused
		elif self.state == STATE['PAUSED']:
			# Pause counters
			self.lvlTime.pause()
			VisualEffectManager.getInstance().pauseCounter()
			# Unpause when player release SPACE
			if eventManager.spacePressed:
				self.state = STATE['IN_PROGRESS']


		# When beginning or life lost
		elif self.state == STATE['NEW_LIFE']:
			# Pause counters
			self.lvlTime.pause()
			VisualEffectManager.getInstance().pauseCounter()
			# Waiting player press SPACE
			if eventManager.spacePressed:
				self.state = STATE['IN_PROGRESS']


		# When counting score
		elif self.state == STATE['SCORE_COUNTING']:
			# Pause counters
			self.lvlTime.pause()
			VisualEffectManager.getInstance().pauseCounter()

			# Increasing total score
			if self.scoreToIncrease < self.players[0].totalScore:
				self.sound.play("scoreCounting.wav")
				self.scoreToIncrease += 1
			# Score to increase reached total score, or negative score
			else:
				self.scoreToIncrease = self.players[0].totalScore

			# Waiting player presses SPACE or score counting finished => force total score
			if eventManager.spacePressed or self.scoreToIncrease == self.players[0].totalScore:
				self.scoreToIncrease = self.players[0].totalScore
				self.state = STATE['SCORE_END']
				# New record sound
				if self.isNewRecord:
					self.sound.play("new_record.ogg")


		# When score counting ends
		elif self.state == STATE['SCORE_END']:
			# Waiting player presses SPACE => level end or game over
			if eventManager.spacePressed:
				self.state = self.stateAfterScore


		# When level finished => start counting score
		elif self.state == STATE['LEVEL_END']:
			self.currentLvl += 1
			for p in self.players:
				if p.lives < NB_LIVES['MAX']:
					p.lives += 1
			# Load next level if exists
			if self.currentLvl < len(self.levels):
				self.initLevel(self.currentLvl, self.directory)
			# Game finished otherwise
			else:
				self.state = STATE['GAME_END']


		# When game end => ask player for restart
		elif self.state == STATE['GAME_OVER'] or self.state == STATE['GAME_END'] :
			# Pause counters
			self.lvlTime.pause()
			VisualEffectManager.getInstance().pauseCounter()

			# Y => reset game state
			if eventManager.yPressed:
				Player.initId()
				return True, True
			# N => quit game
			if eventManager.nPressed:
				# for reentrance
				Player.OBJECT_INDEX = 0
				return True, False

		return False, False


	def manageGame(self, eventManager):
		super(GameStateSingleAdventure, self).manageGame(eventManager)

		# Debug
		if DEBUG:
			key = pygame.key.get_pressed()
			if key[K_n]:
				self.state = STATE['LEVEL_END']
			if key[K_l]:
				self.players[0].lives += 1
				if self.players[0].lives > NB_LIVES['MAX']:
					self.players[0].lives = NB_LIVES['MAX']

		# Collisions
		paddles = [p.paddle for p in self.players]
		self.ch.loadState(self.grid, self.balls, paddles)
		brickHit, ballTouchesGround, uEffectsPad, hitPad, ballWall = self.ch.checkAllCollisions()
		self.ch.saveState(self.grid, self.balls, paddles)

		if ballWall:
			self.sound.play("ballWall.wav")

		# Reset chain bonus when pad hit
		if hitPad:
			self.chainBonus = 0
			self.sound.play("ballPad.ogg")

		# if all non negative bricks are removed
		# change negative bricks to normal bricks
		convertNeg = True
		for b in self.grid.bricks:
			if b.bType < 4 or b.bType > 6:
				convertNeg = False
		if convertNeg:
			for b in self.grid.bricks:
				if b.bType == BRICK_TYPE["DEVIL"] or b.bType == BRICK_TYPE["SATAN"]:
					b.bType = 1
					b.score = NEG_BRICK_POS_SCORE

		# Remove hit bricks
		for brk in brickHit:
			if brk is not None:

				# Satanic effect: all balls suddenly curve
				if self.grid.getType(brk) == BRICK_TYPE["SATAN"]:
					for b in self.balls:
						b.isCurving = 'X'
						randomSign = random.randrange(2)
						if randomSign == 0:
							randomSign = -1
						else:
							randomSign = 1
						b.curve = randomSign * BALL_CURVE_FACTOR/2
				# Devil effect: random direction
				if self.grid.getType(brk) == BRICK_TYPE["DEVIL"]:
					for b in self.balls:
						randomSign = random.randrange(2)
						if randomSign == 0:
							randomSign = -1
						else:
							randomSign = 1
						b.dX = randomSign * random.uniform(sqrt(BALL_SPEED_MAX)/2, sqrt(BALL_SPEED_MAX))
						b.dY = randomSign * random.uniform(sqrt(BALL_SPEED_MAX)/2, sqrt(BALL_SPEED_MAX))
				# Nitro effect: boom
				if self.grid.getType(brk) == BRICK_TYPE["NITRO"]:
					retList = self.grid.explode(brk) # returns list of exploded bricks and spaces
					#print "EXPLODE "+str(retList)
					# special count and indicator to avoid explosion mess
					# Update level and total scores
					self.players[0].scores[0].value += len(retList) * 2
					self.players[0].totalScore += len(retList) * 2
					VisualEffectManager.getInstance().add(ScoreVEF(value='+'+str(len(retList) * 2), posX=(1+2*brk[0])*BRICK_WIDTH/2, posY=(1+2*brk[1])*BRICK_HEIGHT/2))
				# Massive effect: explode in a line
				if self.grid.getType(brk) == BRICK_TYPE["MASSIVE"]:
					defaultBall = self.balls[0] # TODO multiplayer version
					d = self.grid.getDirection(defaultBall.posX, defaultBall.posY, defaultBall.radius*2, defaultBall.radius*2, brk[0]*BRICK_WIDTH+BRICK_WIDTH/2, brk[1]*BRICK_HEIGHT+BRICK_HEIGHT/2)
					retList = self.grid.explode(brk, direction=d) # returns list of exploded bricks and spaces
					#print "MASSIVE "+str(retList)
					# special count and indicator to avoid explosion mess
					# Update level and total scores
					self.players[0].scores[0].value += len(retList) * 2
					self.players[0].totalScore += len(retList) * 2
					VisualEffectManager.getInstance().add(ScoreVEF(value='+'+str(len(retList) * 2), posX=(1+2*brk[0])*BRICK_WIDTH/2, posY=(1+2*brk[1])*BRICK_HEIGHT/2))
				
				# Sound effect
				t = self.grid.getType(brk)
				if t == BRICK_TYPE["NORMAL"]:
					self.sound.play("brickHit.ogg")
				elif t == BRICK_TYPE["STEEL"]:
					self.sound.play("indestructibleHit.ogg")
				else:
					self.sound.play("metalBounce.ogg")

				self.brkScore, self.chainBonus, remainBrick = self.grid.hitBrick(brk, self.chainBonus)
				# Update level and total scores
				self.players[0].scores[0].value += self.brkScore
				self.players[0].totalScore += self.brkScore
				# Add chain bonus
				self.players[0].scores[0].value += SCORE_CHAIN_BONUS[self.chainBonus]
				self.players[0].totalScore += SCORE_CHAIN_BONUS[self.chainBonus]
				# Add game indicator
				if self.brkScore+SCORE_CHAIN_BONUS[self.chainBonus] > 0:
					VisualEffectManager.getInstance().add(ScoreVEF(value='+'+str(self.brkScore+SCORE_CHAIN_BONUS[self.chainBonus]), posX=(1+2*brk[0])*BRICK_WIDTH/2, posY=(1+2*brk[1])*BRICK_HEIGHT/2))
				if self.brkScore < 0:
					VisualEffectManager.getInstance().add(ScoreVEF(value=str(self.brkScore), posX=(1+2*brk[0])*BRICK_WIDTH/2, posY=(1+2*brk[1])*BRICK_HEIGHT/2, color=VEF_NEG_TXT_COLOR))
				
				# Level finished check
				if remainBrick == 0:
					self.state = STATE['SCORE_COUNTING']
					self.stateAfterScore = STATE['LEVEL_END']
					# Add bonus to score
					self.addBonusScore()
					# Store player time for the current lvl
					self.storeLvlTime()
					# Get best player trophy for current lvl
					self.lvlTrophy = self.getLvlBestTrophy()

				else:
					STATE['IN_PROGRESS']


		# Apply effect of usable
		if uEffectsPad[0]['uIndex'] is not None:
			self.sound.play("objectHit.ogg")
			obj, effectType = self.grid.getUsableEffect(uEffectsPad[0]['uIndex'])

			# Apply effect to pad
			if obj == 'PADDLE':
				self.players[0].paddle.applyEffect(effectType)
			# Apply effect to ball
			elif obj == 'BALL':
				self.balls[0].applyEffect(effectType)
			# Apply effect to player
			elif obj == 'PLAYER':
				self.players[0].applyEffect(effectType)

		# Life lost check
		if ballTouchesGround:
			self.sound.play("lifeLost.ogg")
			self.players[0].lives -= 1
			# Reset ball position and speed
			self.balls[0].reset(posX=self.balls[0].posX0, posY=self.balls[0].posY0)
			# Reset paddle position
			self.players[0].paddle.reset(posX=self.players[0].paddleX0, posY=self.players[0].paddleY0)
			# Check for 0 life game over
			if self.players[0].lives <= 0:
				self.state = STATE['SCORE_COUNTING']
				self.stateAfterScore = STATE['GAME_OVER']
			else:
				self.state = STATE['NEW_LIFE']
			# No perfect bonus
			self.isPerfect = False


	def storeLvlTime(self):
		""" Stores player time if best performance for the current level """
	
		# Get previous best time for the level
		prevTime = self.players[0].getTime(self.grid.hashsum.hexdigest())
		# Get current time for the level
		curTime = self.lvlTime.getFrameNb()

		# If best time => store it to the player's list of times
		if prevTime is None or (prevTime is not None and prevTime-curTime) > 0:
			self.players[0].addTime(curTime, self.grid.hashsum.hexdigest())
			self.players[0].saveTimes()
			#print "NEW PERSONAL BEST"
			self.isNewRecord = "LOCAL"

			# Send to website as potential new world record
			# (the website is responsible for validation!)
			http.setWorldTime(self.grid.hashsum.hexdigest(), curTime)
			# ask again what the world record is, to make sure it was validated
			# server-side
			responseTime = http.getWorldTime(self.grid.hashsum.hexdigest())
			if curTime == int(responseTime):
				self.isNewRecord = "WORLD"
	def getLvlBestTrophy(self):
		""" Returns best trophy won for the current level """
		if self.grid.refTime:
			# Get best time for the level
			bestTime = self.players[0].getTime(self.grid.hashsum.hexdigest())

			# Get matching trophy
			if bestTime:
				for trophy, time in self.grid.refTime.iteritems():
					if Counter.getFrameFromSec(time)-bestTime >= 0:
						return trophy
		return None


	def addBonusScore(self):
		""" Add end level bonus to score """

		# If no life lost => Perfect bonus
		if self.isPerfect:
			self.players[0].addBonus(bonusType=BONUS_TYPE['PERFECT'])

		# If better time than bronze => Time bonus
		if self.grid.refTime:
			timeBonus = int(self.grid.refTime[next(reversed(self.grid.refTime))]-self.lvlTime.getSeconds())
			if timeBonus >= 0:
				self.players[0].addBonus(bonusType=BONUS_TYPE['TIME'], value=timeBonus)

		# Add bonus to total score
		self.players[0].addBonusToTotalScore()


	def draw(self):
		# When score counting print score, level trophy / score counting
		if self.state == STATE['SCORE_COUNTING'] or self.state == STATE['SCORE_END']:
			# Create score board
			self.screen.createScoreBoard()
			# Draw score board
			self.screen.drawScoreBoard(self.players[0].scores, self.scoreToIncrease, self.lvlTime, self.lvlTrophy, self.grid.refTime)
			# When score counting ends and new record => print new record
			if self.state == STATE['SCORE_END'] and self.isNewRecord=="LOCAL":
				self.screen.drawNewRecord()
			if self.state == STATE['SCORE_END'] and self.isNewRecord=="WORLD":
				self.screen.drawNewWorldRecord()
		# Other states
		else:
			# Remove score board 
			self.screen.removeScoreBoard()

		super(GameStateSingleAdventure, self).draw()


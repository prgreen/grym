from paddle import Paddle
from player import Player
from ball import Ball
from brickGrid import BrickGrid
from mainBoard import MainBoard
from screen import Screen
from lib.bunch import Bunch
from collisionHandler import CollisionHandler
from gameState import GameState

from constants import *

import os


class GameStateMultiCoop(GameState):

	def __init__(self, screen, players):
		""" Init state common to all levels """
		super(GameStateMultiCoop, self).__init__(screen)

		self.players = [Player(p) for p in players]
		# Only one active pad
		self.activePadId = 0

		# Parse directory to get levels
		self.levels = [lvl for lvl in os.listdir(LVL_DIR) if lvl.endswith(LVL_FORMAT)]
		self.currentLvl = 0
		self.initLevel(self.currentLvl)


	def initLevel(self, lvlIndex):
		""" Construct level with one ball multi player """
		super(GameStateMultiCoop, self).initLevel(self.currentLvl)

		### Construct objects ###
		self.balls = []

		# Init Paddles
		i=1
		for p in self.players:
			posX0 = (self.gameDim[0]-PADDLE_WIDTH['INIT']) * (i/(len(self.players)+1.0))
			posY0 = self.gameDim[1]-3*PADDLE_HEIGHT
			p.initPaddle(padWidth=PADDLE_WIDTH['INIT'], padHeight=PADDLE_HEIGHT, padColor=p.color, padPosX0=posX0, padPosY0=posY0)
			p.paddle.disable() if(i!=self.activePadId+1) else p.paddle.enable()
			i+=1

		# Ball
		posX0 = (self.gameDim[0]-BALL_RADIUS) /2
		posY0 = self.gameDim[1]/4
		self.balls.append(Ball(radius=BALL_RADIUS, posX=posX0 , posY=posY0, color=BALL_COLOR))

		### Concatenate objects ###
		for i in reversed(range(len(self.players))):
			self.objects.append(self.players[i].paddle)
		for b in self.balls:
			self.objects.append(b)


	def update(self, eventManager):
		super(GameStateMultiCoop, self).update()

		# TODO: enable pause with restrictions?

		# When level in progress
		if self.state == STATE['IN_PROGRESS']:
			self.lvlTime.unpause()
			self.manageGame(eventManager)


		# When beginning or life lost
		elif self.state == STATE['NEW_LIFE']:
			self.lvlTime.pause()
			# Waiting player press SPACE
			if eventManager.spacePressed:
				self.state = STATE['IN_PROGRESS']

		# TODO: handle GAME_END state

		# When level finished => load next level
		if self.state == STATE['LEVEL_END']:
			self.lvlTime.pause()
			self.currentLvl += 1

			# Load next level if exists
			if self.currentLvl < len(self.levels):
				self.initLevel(self.currentLvl)
			# Game finished otherwise
			else:
				self.state = STATE['GAME_END']

		# When game over => ask player for restart
		elif self.state == STATE['GAME_OVER'] or self.state == STATE['GAME_END']:
			self.lvlTime.pause()
			# Y => reset game state
			if eventManager.yPressed:
				Player.initId()
				return True, True
			# N => quit game
			if eventManager.nPressed:
				return True, False

		return False, False



	def manageGame(self, eventManager):
		super(GameStateMultiCoop, self).manageGame(eventManager)

		# Collisions
		paddles = [p.paddle for p in self.players]
		self.ch.loadState(self.grid, self.balls, paddles)
		brickHit, ballTouchesGround, uEffectsPad, hitPad = self.ch.checkAllCollisions(self.activePadId)
		self.ch.saveState(self.grid, self.balls, paddles)

		# If hit pad => active next pad
		if hitPad:
			self.chainBonus = 0
			self.activePadId = (self.activePadId + 1) % len(self.players)

			for i in range(len(self.players)):
				self.players[i].paddle.disable() if(i!=self.activePadId) else self.players[i].paddle.enable()
				

		# Remove hit bricks
		for brk in brickHit:
			if brk is not None:
				bonus, self.chainBonus, remainBrick = self.grid.hitBrick(brk, self.chainBonus)
				for p in self.players:
					p.score += bonus
					# Add chain bonus
					p.score += SCORE_CHAIN_BONUS[self.chainBonus]
				# Level finished check
				self.state = STATE['LEVEL_END'] if remainBrick == 0 else STATE['IN_PROGRESS']


		# Apply effect of usables
		for u in uEffectsPad:
			if u['uIndex'] is not None:
				obj, effectType = self.grid.getUsableEffect(u['uIndex'])
				if obj == 'PADDLE':
					self.players[u['padIndex']].paddle.applyEffect(effectType)
				elif obj == 'BALL':
					self.balls[u['padIndex']].applyEffect(effectType)

		# Life lost check
		if ballTouchesGround:
			for p in self.players:
				p.lives -= 1
				# Reset paddle position
				p.paddle.reset(posX=p.paddleX0, posY=p.paddleY0)

			# Reset ball position and speed
			self.balls[0].reset(posX=self.balls[0].posX0, posY=self.balls[0].posY0)

			# Check for 0 life game over
			self.state = STATE['GAME_OVER'] if self.players[0].lives <= 0 else STATE['NEW_LIFE']


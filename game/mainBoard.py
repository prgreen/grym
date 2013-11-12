from screen import Screen
from lib.bunch import Bunch
from counter import Counter
from brickGrid import BrickGrid
from player import Player,Score
from visualEffectManager import VisualEffect

from constants import *


class MainBoard:

	def __init__(self, window):
		""" Inits window, game board and state board """
		self.width = window.get_width()
		self.height = window.get_height()

		self.window = window

		self.screens = {
			'GAMEBOARD': Screen(window=self.window, x0=self.width/4, y0=0, width=3*self.width/4, height=self.height, color=BG_COLOR),
			'STATEBOARD': Screen(window=self.window, x0=0, y0=0, width=self.width/4, height=self.height, color=MENU_BG_COLOR)
		}


	def drawAllBG(self, lvlBGColor):
		""" Draw all screens backgrounds """
		self.screens['STATEBOARD'].drawBG()
		self.screens['GAMEBOARD'].drawBG(lvlBGColor)


	### MESSAGES ###
	def drawPressToContinue(self):
		""" Print 'press to continue' message on game board """
		scr = self.screens['GAMEBOARD']
		scr.drawText(text=RESUME_LBL, color=GLOBAL_LABEL_COLOR, size=RESUME_LBL_SZ, posX=0, posY=0, bold=1, alignH=TEXT_ALIGN['H']['CENTER'], alignV=TEXT_ALIGN['V']['MIDDLE'], border=True)


	### GAMEOVER ###
	def createGameOver(self):
		""" Creates and inits gameover surface """
		if 'GAMEOVER' not in self.screens:
			self.screens['GAMEOVER'] = Screen(window=self.window, x0=self.width/4+BRICK_WIDTH, y0=2*self.height/5, width=3*self.width/4-(BRICK_WIDTH*2), height=self.height/5, color=SCORE_BG_COLOR)

	def drawGameOver(self):
		""" Prints 'game over' message """
		scr = self.screens['GAMEOVER']
		# Background
		scr.drawBG()

		posY = MENU_SPACE_M
		# Game over label	
		scr.drawText(text=GO_LBL, color=GLOBAL_LABEL_COLOR, size=GO_LBL_SZ, posX=0, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['CENTER'], border=True)
		# Restart game label
		scr.drawText(text=GO_RESTART_LBL, color=GLOBAL_LABEL_COLOR, size=GO_RESTART_LBL_SZ, posX=0, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['CENTER'], alignV=TEXT_ALIGN['V']['BOTTOM'], border=True)

	def removeGameOver(self):
		""" Removes game over from list of screens """ 
		if 'GAMEOVER' in self.screens:
			del self.screens['GAMEOVER']


	### GAMEBOARD ###
	def getGameDim(self):
		""" Returns width and height of game board """
		scr = self.screens['GAMEBOARD']
		return scr.width, scr.height

	def drawObjects(self, objects):
		""" Draws objects on game board """
		scr = self.screens['GAMEBOARD']
		for o in objects:
			o.draw(scr)

	def drawVisualEffects(self, viList):
		""" Draws game indicators on game board """
		scr = self.screens['GAMEBOARD']
		for vi in viList:
			vi.draw(scr)


	### SCOREBOARD ###
	def createScoreBoard(self):
		""" Creates and inits score board """
		if 'SCOREBOARD' not in self.screens:
			self.screens['SCOREBOARD'] = Screen(window=self.window, x0=self.width/4+BRICK_WIDTH, y0=BRICK_WIDTH, width=3*self.width/4-(BRICK_WIDTH*2), height=self.height-(BRICK_WIDTH*2), color=SCORE_BG_COLOR, alpha=200)			

	def drawScoreBoard(self, scores, totalScore, lvlTime, trophy, refTime):
		""" Prints data on score board """
		scr = self.screens['SCOREBOARD']

		# Background
		scr.drawBG()

		posX = MENU_SPACE_M*3
		posY = MENU_SPACE_M*6

		### SCORE ###
		for s in scores:
			# Player score
			scr.drawText(text=Score.formatScore(s), color=SCORE_LBL_COLOR, size=BONUS_SZ, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
			# Score level label
			posY = scr.drawText(text=s.label, color=SCORE_LBL_COLOR, size=BONUS_SZ, posX=posX, posY=posY, bold=1)
			posY += MENU_SPACE_S
		# Player total score
		scr.drawText(text=str(totalScore), color=SCORE_LBL_COLOR, size=SCORE_SZ, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
		# Total score label 
		posY = scr.drawText(text=SCORE_TOTAL_LBL, color=SCORE_LBL_COLOR, size=SCORE_SZ, posX=posX, posY=posY, bold=1)
		
		### TIME ###
		# Player time
		posY += MENU_SPACE_M
		scr.drawText(text=lvlTime.formatCounter(), color=SCORE_LBL_COLOR, size=TIME_SZ, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
		# Time label
		posY = scr.drawText(text=MENU_TIME_LBL, color=SCORE_LBL_COLOR, size=TIME_SZ, posX=posX, posY=posY, bold=1)
		
		### TROPHY ###
		# Player trophy
		posY = scr.height/2 + MENU_SPACE_M
		if trophy is not None:
			posY = scr.drawText(text=trophy, color=SCORE_LBL_COLOR, size=RESUME_LBL_SZ, posX=0, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['CENTER'])
		else:
			posY = scr.drawText(text=NO_TROPHY_LBL, color=SCORE_LBL_COLOR, size=RESUME_LBL_SZ, posX=0, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['CENTER'])

		# Level time reference
		posY += MENU_SPACE_M
		if refTime:
			for tro, time in refTime.iteritems():
				color = TROPHY_PLAYER_COLOR if tro == trophy else SCORE_LBL_COLOR
				# Reference time 
				scr.drawText(text=Counter.formatTime(time*1000), color=color, size=TROPHY_REF_SZ, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
				# Trophy label
				posY = scr.drawText(text=tro, color=color, size=TROPHY_REF_SZ, posX=posX, posY=posY, bold=1)
				posY += MENU_SPACE_S


	def drawNewRecord(self):
		""" Prints 'New record' message on score board """
		scr = self.screens['SCOREBOARD']

		posY = MENU_SPACE_M
		# New record label	
		scr.drawText(text=NEW_RECORD_LBL, color=GLOBAL_LABEL_COLOR, size=NEW_RECORD_SZ, posX=0, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['CENTER'], blink=True)
		
	def drawNewWorldRecord(self):
		""" Prints 'World record' message on score board """
		scr = self.screens['SCOREBOARD']

		posY = MENU_SPACE_M
		# New record label	
		scr.drawText(text=WORLD_RECORD_LBL, color=GLOBAL_LABEL_COLOR, size=NEW_RECORD_SZ, posX=0, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['CENTER'], blink=True)
				
	def removeScoreBoard(self):
		""" Remove score board from list of screens """ 
		if 'SCOREBOARD' in self.screens:
			del self.screens['SCOREBOARD']


	### STATEBOARD ###
	def drawStateBoard(self, grid, players, lvlTime, localRecord, worldRecord):
		""" Prints data on state board """
		scr = self.screens['STATEBOARD']
		posX = MENU_SPACE_S
		posY = MENU_SPACE_M

		### LEVEL METADATA ###
		# Level label
		posY = scr.drawText(text=MENU_LEVEL_LBL, color=GLOBAL_LABEL_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)
		# Level title
		posY = scr.drawText(text=grid.lvlName, color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)
		# Author label
		posY += MENU_SPACE_M
		posY = scr.drawText(text=MENU_AUTHOR_LBL, color=GLOBAL_LABEL_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)
		# Level author
		posY = scr.drawText(text=grid.lvlAuthor, color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)


		### PLAYER INFO ###
		posY += MENU_SPACE_M*2
		for p in players:
			# Name
			posY += MENU_SPACE_M
			posY = scr.drawText(text=p.name, color=p.color, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)

			# Lives icons
			posY += MENU_SPACE_S
			for i in range (p.lives):
				obj = Bunch(posX=scr.width-MENU_SPACE_S-(BALL_RADIUS+i*(BALL_RADIUS*2+MENU_SPACE_S)), posY=posY+BALL_RADIUS, radius=BALL_RADIUS, color=p.color, border=False)
				scr.drawObject(obj, SHAPE['CIRCLE'])
			# Lives label
			posY = scr.drawText(text=MENU_LIVES_LBL, color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_XS, posX=posX, posY=posY, bold=1)

			# Level score value
			posY += MENU_SPACE_S
			scr.drawText(text=str(p.scores[0].value), color=p.color, size=MENU_LBL_SZ_XS, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
			# Level score label
			posY = scr.drawText(text=SCORE_LVL_LBL, color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_XS, posX=posX, posY=posY, bold=1)
			# Total score value
			posY += MENU_SPACE_S
			scr.drawText(text=str(p.totalScore), color=p.color, size=MENU_LBL_SZ_XS, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
			# Level score label
			posY = scr.drawText(text=SCORE_TOTAL_LBL, color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_XS, posX=posX, posY=posY, bold=1)

		### TIME ###
		posY += MENU_SPACE_M*4
		# Time value
		scr.drawText(text=str(lvlTime.formatCounter(2)), color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
		# Time label
		scr.drawText(text=MENU_TIME_LBL, color=GLOBAL_LABEL_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)
		# Local Record
		if localRecord:
			posY += MENU_SPACE_M*2
			scr.drawText(text=str(Counter.staticFormat(localRecord, 2)), color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
			scr.drawText(text=MENU_LOCAL_TIME_LBL, color=GLOBAL_LABEL_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)
		# World Record
		if worldRecord:
			posY += MENU_SPACE_M*2
			scr.drawText(text=str(Counter.staticFormat(worldRecord, 2)), color=GLOBAL_MENU_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1, alignH=TEXT_ALIGN['H']['RIGHT'])
			scr.drawText(text=MENU_WORLD_TIME_LBL, color=GLOBAL_LABEL_COLOR, size=MENU_LBL_SZ_S, posX=posX, posY=posY, bold=1)
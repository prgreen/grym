from paddle import Paddle

from constants import(
	PLAYERS_DIR,
	PLAYER_COLOR,
	NB_LIVES,
	SCORE_LVL_LBL,
	BONUS_TYPE,
	BONUS_INDEX,
	USABLE_TYPE,
	BONUS)
import os

class Score:

	def __init__(self, label, factor=1, value=0):
		self.factor = factor
		self.value = value
		self.label = label

	def formatScore(self):
		""" Returns formatted printable string for score """
		frmScore = ''

		# 3 digits for factor
		for i in range(3-len(str(self.factor))):
			frmScore += '0'
		frmScore += str(self.factor)

		frmScore += 'x'
		# 7 digits for bonus score
		for i in range(7-len(str(self.value))):
			frmScore += '0'
		frmScore += str(self.value)

		return frmScore


class Player:

	OBJECT_INDEX = 0

	def __init__(self, playerName):

		self.id = Player.OBJECT_INDEX
		self.color = PLAYER_COLOR[self.id]
		self.totalScore = 0
		self.scores = []
		self.name = playerName
		self.lives = NB_LIVES['INIT']

		self.timesFrm = {}
		self.loadTimes()
		
		Player.OBJECT_INDEX += 1

	def initPaddle(self, padWidth, padHeight, padColor, padPosX0, padPosY0):
		self.paddleX0 = padPosX0
		self.paddleY0 = padPosY0
		self.paddle = Paddle(width=padWidth, height=padHeight, posX=self.paddleX0, posY=self.paddleY0, color=padColor)


	def initScore(self):
		""" Empties list of scores and init level score """
		del self.scores[:]
		self.scores.append(Score(label=SCORE_LVL_LBL, factor=1, value=0))

	def addBonus(self, bonusType, factor=1, value=0):
		""" Adds bonus to the list of scores """
		lbl = BONUS[bonusType][BONUS_INDEX['LBL']]
		val = value if BONUS[bonusType][BONUS_INDEX['VALUE']] == 'value' else BONUS[bonusType][BONUS_INDEX['VALUE']]
		self.scores.append(Score(label=lbl, factor=factor, value=val))

	def addBonusToTotalScore(self):
		""" Adds values of the list of bonus to total score """
		for s in self.scores[1:]:
			self.totalScore += (s.value*s.factor)

	def applyEffect(self, effectType):
		""" Applies effect to player """
		# PLA_LIFEUP: Add 1 life
		if effectType == USABLE_TYPE['PLA_LIFEUP']:
			self.addLife()
			self.paddle.applyEffect(effectType)


	def addLife(self):
		self.lives = self.lives+1 if self.lives < NB_LIVES['MAX'] else NB_LIVES['MAX']


	@staticmethod
	def initId():
		Player.OBJECT_INDEX = 0


	def addTime(self, timeFrm, lvlId):
		""" Adds time (frame number) for a level to the list of player's times """
		self.timesFrm[lvlId] = timeFrm
		

	def getTime(self, lvlId):
		""" Returns existing time (frame number) for a level, None else """
		if lvlId in self.timesFrm:
			return self.timesFrm[lvlId]

		return None
		
	def ensureDir(self, f):
		d = os.path.dirname(f)
		if not os.path.exists(d):
			os.makedirs(d)
			
	def loadTimes(self):
		self.ensureDir(PLAYERS_DIR)
		try:
			with open(PLAYERS_DIR+self.name) as f:
				lines = f.read()
				for line in lines.split('\n'):
					if line != '':
						l = line.split('|')
						self.timesFrm[l[0]] = int(l[1])
				f.close()
		except IOError:
			pass

	def saveTimes(self):
		f = open(PLAYERS_DIR+self.name, 'w')
		for k,v in self.timesFrm.iteritems():
			f.write(str(k)+'|'+str(v)+'\n')
		f.close()


# TODO
# Store / load player's trophy history
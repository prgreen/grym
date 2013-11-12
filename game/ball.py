from gameObject import GameObject
from math import sqrt
from constants import *


class Ball(GameObject):

	def __init__(self, radius, posX=0, posY=0, color=DEFAULT_COLOR):

		super(Ball, self).__init__(posX, posY, color)
		self.radius = radius

		self.posX0 = posX
		self.posY0 = posY

		# Init speed
		self.dX = 1
		self.dY = 1

		# Curve effect speed (horizontal speed)
		self.isCurving = None #can be "X" or "Y"
		self.curve = 0
		 


	def reset(self, posX, posY):
		super(Ball, self).reset(posX, posY)
		self.dX = 1
		self.dY = 1
		self.isCurving = None
		self.curve = 0


	def applyEffect(self, effectName):
		pass


	def update(self):
		self.posX += self.dX
		self.posY += self.dY

		if self.isCurving:
			self.color = BALL_CURVING_COLOR
			mag = sqrt(self.dX * self.dX + self.dY * self.dY)
			if self.isCurving == "X":
				self.dX += self.curve
			elif self.isCurving == "Y":
				self.dY += self.curve

			newMag = sqrt(self.dX * self.dX + self.dY * self.dY)
			self.dX *= mag/newMag
			self.dY *= mag/newMag
		else:
			self.color = BALL_COLOR


	def draw(self, screen):

		super(Ball, self).draw(screen, SHAPE['CIRCLE'])
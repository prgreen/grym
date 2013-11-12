from screen import Screen

from constants import *


class GameObject(object):

	OBJECT_INDEX = 0

	def __init__(self, posX=0, posY=0, color=DEFAULT_COLOR):

		self.posX = posX
		self.posY = posY
		self.color = color

		self.index = GameObject.OBJECT_INDEX
		GameObject.OBJECT_INDEX += 1


	def reset(self, posX=0, posY=0):
		self.posX = posX
		self.posY = posY


	def update(self):
		pass


	def draw(self, screen, shape):

		screen.drawObject(self, shape)
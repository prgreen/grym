from gameObject import GameObject

from constants import(USABLE_DIM,
	USABLE_TYPE,
	USABLE_CHAR_INDEX,
	USABLE_CHAR,
	SHAPE)


class Usable(GameObject):

	def __init__(self, bIndex, posX=0, posY=0, uType=0):

		self.width = USABLE_DIM
		self.height = USABLE_DIM
		self.uType = uType
		self.isFalling = False

		# Index of matching brick
		self.bIndex = bIndex

		# Init char
		self.dY = USABLE_CHAR[self.uType][USABLE_CHAR_INDEX['SPEED']]
		self.color = USABLE_CHAR[self.uType][USABLE_CHAR_INDEX['COLOR']]

		super(Usable, self).__init__(posX-self.width/2, posY, self.color)


	def getEffect(self):
		return USABLE_CHAR[self.uType][USABLE_CHAR_INDEX['TO']], self.uType


	def setFalling(self):
		self.isFalling = True


	def update(self):
		self.posY += self.dY


	def draw(self, screen):

		super(Usable, self).draw(screen, SHAPE['RECT'])


# TODO
# Increase boost
# Increase number of balls
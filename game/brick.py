from gameObject import GameObject

from constants import(BRICK_TYPE,
	BRICK_CHAR_INDEX,
	BRICK_CHAR,
	BRICK_WIDTH,
	BRICK_HEIGHT,
	SCORE_BONUS_MIN,
	SHAPE)


class Brick(GameObject):

	def __init__(self, index, posX=0, posY=0, bType=BRICK_TYPE['NORMAL']):

		self.width = BRICK_WIDTH
		self.height = BRICK_HEIGHT
		self.bType = bType
		self.resistance = BRICK_CHAR[self.bType][BRICK_CHAR_INDEX['RES']]
		self.score = BRICK_CHAR[self.bType][BRICK_CHAR_INDEX['BONUS']]
		self.bIndex = index

		self.setColor()

		super(Brick, self).__init__(posX, posY, self.color)


	def hit(self):
		""" Decrease brick resistance """
		if self.resistance > 0:
			self.resistance -= 1

		# Send score when brick destroyed
		score = self.score if self.resistance <= 0 else SCORE_BONUS_MIN
		return self.resistance, score


	def setColor(self):
		""" Update brick color from resistance """
		# Get new color from updated resistance
		self.color = BRICK_CHAR[self.bType][BRICK_CHAR_INDEX['COLOR']]
		if self.bType < 4:
			newType = self.resistance if self.resistance >= 0  else self.resistance
			self.color = BRICK_CHAR[newType][BRICK_CHAR_INDEX['COLOR']]


	def update(self):
		# Update brick color
		self.setColor()


	def draw(self, screen):

		super(Brick, self).draw(screen, SHAPE['RECT'])
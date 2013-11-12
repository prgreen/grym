import pygame

class Sprite:

	def __init__(self, surface):
		self.surface = surface.copy()

	def replaceColor(self, colorFrom, colorTo):
		""" Replaces color in image """
		#pygame.transform.threshold(self.surface, self.surface, colorFrom, (0,0,0,0), colorTo, 2, self.surface, True)
		pygame.PixelArray(self.surface).replace(colorFrom, colorTo)

	def imageAt(self, rectangle, colorKey=None):
		""" Returns sprite surface from a specific rectangle
		Param colorKey: Set to -1 to define 1st pixel of image file as transparent color
		"""
		rect = pygame.Rect(rectangle)
		image = pygame.Surface(rect.size).convert()

		# Get part of image file
		image.blit(self.surface, (0, 0), rect)

		# Set alpha color
		if colorKey is not None:
			if colorKey == -1:
				colorKey = image.get_at((0,0))
			image.set_colorkey(colorKey, pygame.RLEACCEL)

		return image

	def imagesAt(self, rects, colorKey=None):
		""" Returns list of sprite surfaces
		Param colorKey: Set to -1 to define 1st pixel of image file as transparent color
		"""
		return [self.imageAt(rect, colorKey) for rect in rects]

	def loadStrip(self, spriteNb=2, offsetX=0, width=-1, colorKey=None):
		""" Loads n regular sprites
		Param spriteNb: Number of strip, 2 by default
		Param width:    Strip width, image file width/2 by default
		Param colorKey: Set to -1 to define 1st pixel of image file as transparent color
		"""
		# Set strip width
		if width == -1:
			width = self.surface.get_width()/2

		height = self.surface.get_height()
		tups = [(offsetX+width*i, 0, width, height) for i in range(spriteNb)]
		return self.imagesAt(tups, colorKey)


class SpriteManager:

	_instance = None

	def __init__(self, imgFolder):
		self._images = {}
		self._imageFolder = imgFolder

	@staticmethod
	def getInstance(imgFolder=""):
		if SpriteManager._instance is None:
			SpriteManager._instance = SpriteManager(imgFolder)

		return SpriteManager._instance

	def getSprite(self, imgName):
		""" Returns new instance Sprite from image """ 
		if imgName in self._images.iterkeys():
			return Sprite(self._images[imgName])

		return None

	def load(self, img):
		""" Adds/updates image """ 
		self._images[img] = pygame.image.load(self._imageFolder+img).convert()

	def loadAllImages(self):
		""" Load all images """
		self.load("pad_arrows.png")
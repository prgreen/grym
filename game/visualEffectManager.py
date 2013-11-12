from screen import Screen
from counter import Counter
from spriteManager import Sprite, SpriteManager
from lib.bunch import Bunch


from constants import (SCORE_SZ,
	VEF_TXT_COLOR,
	VEF_TXT_SZ,
	VEF_SCORE_TIMER,
	VEF_PAD_GROW_COLOR,
	VEF_PAD_GROW_TIMER,
	VEF_PAD_SHRINK_COLOR,
	VEF_PAD_LBL_COLOR,
	DEF_ALPHA_COLOR,
	TEXT_ALIGN
)

### VISUAL EFFECT BASE CLASS ###
class VisualEffect(object):

	def __init__(self, content, posX=0, posY=0):
		self.content = content
		self.posX = posX
		self.posY = posY
		self.isFinished = False

	def update(self):
		pass

	def draw(self):
		""" Draws visual effect """
		pass

### VISUAL EFFECT POSITION INTERFACES ###
class FreePosEffect(object):
	""" Interface for effect without bound position """
	def initPosition(self, posX, posY):
		self.posX = posX
		self.posY = posY

class FollowingPosEffect(object):
	""" Interface for effect following reference object """
	def initReference(self, ref):
		self.ref = ref
		self.posX = ref.posX
		self.posY = ref.posY

### VISUAL EFFECT TRIGGER INTERFACE ###
class TemporaryEffect(object):
	""" Interface for temporary effect """
	def start(self, ms):
		self.counter = Counter(ms)
		self.counter.start() 
		self.isFinished = False

	def update(self):
		# Visual effect finished when counter elapsed
		if self.counter.timeOut():
			self.isFinished = True


### VISUAL EFFECT TYPE INTERFACE ###
class TextTypeVisualEffect(VisualEffect):
	""" Text visual effect base class """
	def __init__(self, text, size, color, alignH=TEXT_ALIGN['H']['LEFT'], alignV=TEXT_ALIGN['V']['TOP'], refRect=None):
		super(TextTypeVisualEffect, self).__init__(content=text)
		self.size = size
		self.color = color
		self.alignH = alignH
		self.alignV = alignV
		self.refRect = refRect

	def draw(self, screen):
		""" Draws text visual effect """
		screen.drawText(text=self.content, color=self.color, size=self.size, posX=self.posX, posY=self.posY, bold=1, border=True, refRect=self.refRect, alignH=self.alignH, alignV=self.alignV)


class DrawingTypeVisualEffect(VisualEffect):
	""" Drawing visual effect base class """
	def __init__(self, shape, obj):
		super(DrawingTypeVisualEffect, self).__init__(content=obj)
		self.shape = shape

	def draw(self, screen):
		""" Draws drawing visual effect """
		screen.drawObject(obj=self.content, shape=self.shape, bold=1, border=True)


class SpritesTypeVisualEffect(VisualEffect):
	""" Sprites file visual effect base class """
	def __init__(self, imgName, stripWidth=None, rects=None, colors=None, colorKey=None):
		""" Loads sprites from file
		Param imgFile:		Path of image file
		Param stripWidth: 	Width or strips to get sprites
		Param rects:		List of rectangles to get sprites
		Param colors:		Tuple (colorFrom, colorTo)
		Param colorKey:		Transparent color
		"""
		### FILE ###
		# Get image
		img = SpriteManager.getInstance().getSprite(imgName=imgName)
		# If colors defined => replace color 
		if colors is not None:
			img.replaceColor(colors[0], colors[1])

		### SPRITES ###
		# If stripWidth defined => get sprites by width 
		if stripWidth is not None:
			sprites = img.loadStrip(width=stripWidth, colorKey=colorKey)
		# If rects defined => get sprites by rects
		elif rects is not None:
			sprites = img.imagesAt(rects=rects, colorKey=colorKey)
		# Otherwise => sprite = full image
		else:
			sprites = [img]

		content = [Bunch(surface=s, posX=0, posY=0) for s in sprites]
		super(SpritesTypeVisualEffect, self).__init__(content=content)

	def draw(self, screen):
		""" Prints image visual effect """
		# Print all sprites
		for s in self.content:
			screen.drawSprite(s.surface, s.posX, s.posY)


### VISUAL EFFECT IMPLEMENTATIONS ###
class ScoreVEF(TemporaryEffect, FreePosEffect, TextTypeVisualEffect):
	""" Temporary score notification """
	def __init__(self, value, posX=0, posY=0, size=VEF_TXT_SZ, color=VEF_TXT_COLOR):
		super(ScoreVEF, self).__init__(text=value, size=size, color=color)
		FreePosEffect.initPosition(self, posX=posX, posY=posY)
		TemporaryEffect.start(self, ms=VEF_SCORE_TIMER)

	def update(self):
		""" Updates position and state """
		# Visual effect finished when counter elapsed
		TemporaryEffect.update(self)

		# Update position according counter
		if self.counter and not self.counter.paused:
			self.posY += 1

# PAD VISUAL EFFECTS
class PadGrowVEF(TemporaryEffect, FollowingPosEffect, SpritesTypeVisualEffect):
	""" Temporary arrays growing pad sprites """
	def __init__(self, refPad, color=VEF_PAD_GROW_COLOR):

		# Get arrows sprites from file
		super(PadGrowVEF, self).__init__(imgName="pad_arrows.png", stripWidth=-1, colors=((255,255,255),color), colorKey=DEF_ALPHA_COLOR)
		FollowingPosEffect.initReference(self, ref=refPad)
		TemporaryEffect.start(self, ms=VEF_PAD_GROW_TIMER)

		# Space between arrows and pad
		self.space = 1	
		# Init position of arrows sprites
		self.leftArrow = self.content[0]
		self.rightArrow = self.content[1]
		self.setPosition()

	def setPosition(self):
		""" Sets arrow position """
		self.leftArrow.posX = self.ref.posX-self.leftArrow.surface.get_width()-self.space
		self.leftArrow.posY = self.ref.posY-(self.leftArrow.surface.get_height()-self.ref.height)/2
		self.rightArrow.posX = self.ref.posX+self.ref.width+self.space
		self.rightArrow.posY = self.ref.posY-(self.rightArrow.surface.get_height()-self.ref.height)/2

	def update(self):
		""" Updates position and state """
		# Visual effect finished when counter elapsed
		TemporaryEffect.update(self)
		# Update position of arrows sprites
		if self.counter and not self.counter.paused:
			self.space += 1
			self.setPosition()

class PadShrinkVEF(TemporaryEffect, FollowingPosEffect, SpritesTypeVisualEffect):
	""" Temporary arrays growing pad sprites """
	def __init__(self, refPad, color=VEF_PAD_SHRINK_COLOR):

		# Get arrows sprites from file
		super(PadShrinkVEF, self).__init__(imgName="pad_arrows.png", stripWidth=-1, colors=((255,255,255),color), colorKey=DEF_ALPHA_COLOR)
		FollowingPosEffect.initReference(self, ref=refPad)
		TemporaryEffect.start(self, ms=VEF_PAD_GROW_TIMER)

		# Space between arrows and pad
		self.space = 1	
		# Init position of arrows sprites
		self.rightArrow = self.content[0]
		self.leftArrow = self.content[1]
		self.setPosition()

	def setPosition(self):
		""" Sets arrow position """
		self.rightArrow.posX = self.ref.posX+self.ref.width-self.space
		self.rightArrow.posY = self.ref.posY-(self.rightArrow.surface.get_height()-self.ref.height)/2
		self.leftArrow.posX = self.ref.posX-self.leftArrow.surface.get_width()+self.space
		self.leftArrow.posY = self.ref.posY-(self.leftArrow.surface.get_height()-self.ref.height)/2

	def update(self):
		""" Updates position and state """
		# Visual effect finished when counter elapsed
		TemporaryEffect.update(self)
		# Update position of arrows sprites
		if self.counter and not self.counter.paused:
			self.space += 1
			self.setPosition()

class PadNotifVEF(TemporaryEffect, FollowingPosEffect, TextTypeVisualEffect):
	""" Temporary arrays growing pad sprites """
	def __init__(self, refPad, value, size=VEF_TXT_SZ, color=VEF_PAD_LBL_COLOR):
		super(PadNotifVEF, self).__init__(text=value, size=size, color=color, refRect=refPad, alignH=TEXT_ALIGN['H']['CENTER'])
		FollowingPosEffect.initReference(self, ref=refPad)
		TemporaryEffect.start(self, ms=VEF_PAD_GROW_TIMER)

		# Space between text and pad
		self.space = 1
		# Init position of notification
		self.setPosition()

	def setPosition(self):
		""" Sets notification position """
		self.posY = 0-self.size-self.space

	def update(self):
		""" Updates position and state """
		# Visual effect finished when counter elapsed
		TemporaryEffect.update(self)
		# Update position of arrows sprites
		if self.counter and not self.counter.paused:
			self.space += 1
			self.setPosition()


class VisualEffectManager:

	_instance = None

	def __init__(self):
		self.vef = []

	@staticmethod
	def getInstance():
		if VisualEffectManager._instance is None:
			VisualEffectManager._instance = VisualEffectManager()

		return VisualEffectManager._instance


	def getList(self):
		return VisualEffectManager._instance.vef

	def add(self, vef):
		""" Adds a visual effect to the main list """
		self.vef.append(vef)


	def update(self):
		""" Updates list of visual effects """

		# Remove finished visual effect
		for vef in list(self.vef):
			if vef.isFinished:
				self.vef.remove(vef)

		# Update visual effect
		for vef in list(self.vef):
			vef.update()


	def pauseCounter(self):
		""" Pauses counters of all temporary effects """
		for vef in self.vef:
			if issubclass(TemporaryEffect, type(vef)):
				vef.counter.pause()


	def unpauseCounter(self):
		""" Unpauses counters of all temporary effects """
		for vef in self.vef:
			if issubclass(TemporaryEffect, type(vef)):
				vef.counter.unpause()
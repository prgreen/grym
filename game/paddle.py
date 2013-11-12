from gameObject import GameObject
from screen import Screen
from lib.bunch import Bunch
from visualEffectManager import VisualEffectManager, PadGrowVEF, PadShrinkVEF, PadNotifVEF
from counter import Counter

from constants import(
	DIRECTION,
	DEFAULT_COLOR,
	SHAPE,
	PADDLE_WIDTH,
	PADDLE_HEIGHT,
	PADDLE_H_SPEED,
	PADDLE_V_SPEED,
	PADDLE_GRAVITY,
	PAD_GROWTH,
	PAD_BOOST,
	PAD_BOOST_GAIN,
	PAD_BOOST_FRACTION,
	PAD_BOOST_TXT_SZ,
	PADDLE_TRAIL_LEN,
	VEF_PAD_BOOST_LBL,
	VEF_PAD_SPDUP_LBL,
	VEF_PAD_LIFEUP_LBL,
	BOOST_COLOR,
	H_BOOST_COST,
	H_BOOST_FACTOR,
	USABLE_TYPE,
	PAD_BOTTOM_LIMIT,
	DEFAULT_BORDER_WIDTH,
	TEXT_ALIGN,
	FPS)


class Paddle(GameObject):

	def __init__(self, width, height, color=DEFAULT_COLOR, posX=0, posY=0):

		super(Paddle, self).__init__(posX, posY, color)
		self.width = width
		self.height = height

		# Current speed
		self.dX = 0
		self.dY = 0

		# Boost
		self.boostMax = PAD_BOOST['INIT']
		self.boost = self.boostMax
		self.boostGain = PAD_BOOST_GAIN
		self.isBoosting = None # can be "UP" or "DOWN" or "LEFT" or "RIGHT"

		# Max speed
		self.dXMax = PADDLE_H_SPEED['INIT']
		self.dYMax = PADDLE_V_SPEED['INIT']

		# Disable paddle in coop mode
		self.enabled = True

		# Visual effects
		self.isBoostVEF = False

		# Trail
		self.trail = []
		self.trail.append((self.posX,self.posY))
		self.trailCounter = 0



	def reset(self, posX, posY):
		super(Paddle, self).reset(posX, posY)
		self.width = PADDLE_WIDTH['INIT']
		self.dXMax = PADDLE_H_SPEED['INIT']
		self.dYMax = PADDLE_V_SPEED['INIT']

		self.boostMax = PAD_BOOST['INIT']
		self.boost = self.boostMax
		self.isBoosting = None


	def move(self, dirX, dirY, boostingLeft=False, boostingRight=False):
		
		# Normal move
		self.posX += dirX*self.dXMax

		# Horizontal boost
		if boostingLeft and dirX == DIRECTION['X']['LEFT'] and self.boost > self.boostMax * PAD_BOOST_FRACTION:
			self.isBoosting = 'LEFT'
		elif boostingRight and dirX == DIRECTION['X']['RIGHT'] and self.boost > self.boostMax * PAD_BOOST_FRACTION:
			self.isBoosting = 'RIGHT'		
		# Vertical boost
		elif dirY == DIRECTION['Y']['UP'] and self.boost > self.boostMax * PAD_BOOST_FRACTION:
			self.isBoosting = 'UP'
		elif dirY == DIRECTION['Y']['DOWN'] and self.boost > self.boostMax * PAD_BOOST_FRACTION:
			self.isBoosting = 'DOWN'
		

		if (self.isBoosting == 'UP' or self.isBoosting == 'DOWN') and self.boost > 0:
			self.posY += dirY*self.dYMax
			#self.posY -= PADDLE_GRAVITY # compensate gravity
			self.boost -= 1.0/FPS
			if self.boost < 0:
				self.boost = 0

		if (self.isBoosting == 'LEFT' or self.isBoosting == 'RIGHT') and self.boost > 0:
			self.posX += dirX * self.dXMax * H_BOOST_FACTOR
			self.boost -= H_BOOST_COST/FPS
			if self.boost < 0:
				self.boost = 0


	def idle(self):
		""" Updates pad state when no move """
		self.isBoosting = None 


	def disable(self):
		if self.enabled:
			self.enabled = False

			# Update color 
			cols = (0,)
			for c in self.color:
				col = c-100 if c >= 100 else c
				cols += (col,)
			self.color = cols[1:]

	def enable(self):
		if not self.enabled:
			self.enabled = True

			# Update color 
			cols = (0,)
			for c in self.color:
				col = c+100 if c <= 155 else c
				cols += (col,)
			self.color = cols[1:]


	def applyEffect(self, effectType):

		# PAD_SPEEDUP: Increase paddle speed
		if effectType == USABLE_TYPE['PAD_SPEEDUP']:
			self.dXMax = self.dXMax+1 if self.dXMax+1 <= PADDLE_H_SPEED['MAX'] else PADDLE_H_SPEED['MAX']
			self.dYMax = self.dYMax+1 if self.dYMax+1 <= PADDLE_V_SPEED['MAX'] else PADDLE_V_SPEED['MAX']
			# Visual effect
			VisualEffectManager.getInstance().add(PadNotifVEF(value=VEF_PAD_SPDUP_LBL, refPad=self))
		# PAD_GROW: Increase paddle width
		elif effectType == USABLE_TYPE['PAD_GROW']:
			if self.width+PAD_GROWTH <= PADDLE_WIDTH['MAX']:
				self.width = self.width+PAD_GROWTH
				self.posX -= PAD_GROWTH/2
				# Visual effect
				VisualEffectManager.getInstance().add(PadGrowVEF(refPad=self))
			else:
				self.width = PADDLE_WIDTH['MAX']
		# PAD_SHRINK: Decrease paddle width
		elif effectType == USABLE_TYPE['PAD_SHRINK']:
			if self.width-PAD_GROWTH >= PADDLE_WIDTH['MIN']:
				self.width = self.width-PAD_GROWTH
				self.posX += PAD_GROWTH/2
				# Visual effect
				VisualEffectManager.getInstance().add(PadShrinkVEF(refPad=self))
			else:
				self.width = PADDLE_WIDTH['MIN']
		# PAD_BOOST: Increase paddle max and current boost
		elif effectType == USABLE_TYPE['PAD_BOOST']:
			self.boostMax = self.boostMax+PAD_BOOST_GAIN if self.boostMax+PAD_BOOST_GAIN <= PAD_BOOST['MAX'] else PAD_BOOST['MAX']
			self.boost = self.boost+PAD_BOOST_GAIN if self.boost+PAD_BOOST_GAIN <= self.boostMax else self.boostMax
			# Visual effect
			VisualEffectManager.getInstance().add(PadNotifVEF(value=VEF_PAD_BOOST_LBL, refPad=self))
		# PLA_LIFEUP: Life+1 notification
		elif effectType == USABLE_TYPE['PLA_LIFEUP']:
			# Visual effect
			VisualEffectManager.getInstance().add(PadNotifVEF(value=VEF_PAD_LIFEUP_LBL, refPad=self))



	def update(self):

		# Determines paddle current speed
		self.dX = (self.posX-self.trail[len(self.trail)-1][0])
		self.dY = (self.posY-self.trail[len(self.trail)-1][1])

		# Keep track of last position in pad trail
		if len(self.trail) == PADDLE_TRAIL_LEN:
			self.trail.pop(0)
		self.trailCounter += 1
		if self.trailCounter % 3 == 0:	
			self.trail.append((self.posX, self.posY))

		self.posY += PADDLE_GRAVITY

		# Regain boost when on the ground
		if self.posY >= (PAD_BOTTOM_LIMIT - self.height):
			self.boost += self.boostGain/FPS
			if self.boost > self.boostMax:
				self.boost = self.boostMax

		#print str(self.boost)
		#print self.dX


	def draw(self, screen):

		### BOOST VISUAL EFFECT ###
		if self.isBoosting == 'LEFT' or self.isBoosting == 'RIGHT':
			alp = 20
			for pos in self.trail:
				alp += 20
				obj = Bunch(posX=pos[0], posY=pos[1], width=self.width, height=self.height, color=self.color)
				screen.drawObject(obj=obj, shape=SHAPE['RECT'], border=True, alpha=alp)

		### PAD ###
		super(Paddle, self).draw(screen, SHAPE['RECT'])

		### BOOST BAR ###
		# Boost color
		if self.boost <= self.boostMax * PAD_BOOST_FRACTION:
			col = BOOST_COLOR['OUTOF']
		elif self.posY >= (PAD_BOTTOM_LIMIT - self.height):
			col = BOOST_COLOR['RELOAD']
		else:
			col = BOOST_COLOR['DEFAULT']

		# Draw boost bar
		width = self.boost*self.width/self.boostMax-2*DEFAULT_BORDER_WIDTH
		height = PADDLE_HEIGHT/4
		posX = self.posX + (self.width-width)/2+DEFAULT_BORDER_WIDTH/2
		posY = self.posY + (self.height-PADDLE_HEIGHT/4)/2

		# Rect		
		width = int(self.boost*(self.width-(2*DEFAULT_BORDER_WIDTH))/self.boostMax)
		if width%2 == 1:
			width -= 1
		height = (self.height-2*DEFAULT_BORDER_WIDTH)/3
		posX = self.posX + (self.width-(2*DEFAULT_BORDER_WIDTH)-width)/2 + DEFAULT_BORDER_WIDTH
		posY = self.posY + (self.height-height)/2

		obj = Bunch(posX=posX, posY=posY, width=width, height=height, color=col)
		screen.drawObject(obj=obj, shape=SHAPE['RECT'], border=False)

		# Circle
		posX = self.posX + self.width/2
		posY = self.posY + self.height/2
		obj = Bunch(posX=posX, posY=posY, radius=PADDLE_HEIGHT/3, color=col)
		screen.drawObject(obj=obj, shape=SHAPE['CIRCLE'], border=False)

		### BOOST VALUE ###
		# When boosting => print boost value
		if self.isBoosting is not None:
			screen.drawText(text=str(int(self.boost*10)), size=PAD_BOOST_TXT_SZ, posY=self.height*6/7, refRect=self, alignH=TEXT_ALIGN['H']['CENTER'])


from math import sqrt, cos, sin, pi, tanh
from constants import (BRICK_WIDTH, 
	BRICK_HEIGHT,
	NB_BRICK_BY_ROW_MAX,
	PADDLE_FACTOR,
	BALL_FACTOR,
	BALL_CURVE_FACTOR,
	BALL_RADIUS,
	BALL_SPEED_MIN,
	BALL_SPEED_MAX,
	PADDLE_H_SPEED,
	PAD_BOTTOM_LIMIT,
	GAME_WINDOW_WIDTH,
	GAME_WINDOW_HEIGHT)


class Rect:
	"""x y top left point, w h width height"""
	def __init__(self, x=0, y=0, w=0, h=0):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	@classmethod
	def byCenterHalf(cls, cx, cy, halfw, halfh):
		return cls(cx - halfw, cy - halfh, 2 * halfw, 2 * halfh)
	@classmethod
	def byCenter(cls, cx, cy, w, h):
		return cls(cx - w/2, cy - h/2, w, h)
	def center(self):
		return {'x' : self.x + self.w/2, 'y' : self.y + self.h/2}
	def topleft(self):
		return {'x' : self.x, 'y' : self.y}
	def __str__(self):
		return str({'x':self.x,'y':self.y,'w':self.w,'h':self.h})
	@staticmethod
	def collision(r1, r2):
		return not(r2.x > r1.x + r1.w or
			r2.x + r2.w < r1.x or
			r2.y > r1.y + r1.h or
			r2.y + r2.h < r1.y)

def d2(x1, y1, x2, y2):
	"""distance between two points, squared"""
	return (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)

def getBrickRect(point):
	"""get collision rect from grid coordinate"""
	return Rect(point[0] * BRICK_WIDTH, point[1] * BRICK_HEIGHT, BRICK_WIDTH, BRICK_HEIGHT)

def pvVertical(p, v, x, ymin, ymax):
	"""checks whether prolonging in direction of vector v from point p 
	intersects vertical segment, and returns intersection point if it does"""
	mag = float(x - p['x']) / v['x']
	if mag >=0:
		ys = p['y'] + mag * v['y']
		if ys >= ymin and ys <= ymax:
			return {'x' : x, 'y': int(ys)}
	return None
def pvHorizontal(p, v, y, xmin, xmax):
	"""checks whether prolonging in direction of vector v from point p 
	intersects horizontal segment, and returns intersection point if it does"""
	mag = float(y - p['y']) / v['y']
	if mag >=0:
		xs = p['x'] + mag * v['x']
		if xs >= xmin and xs <= xmax:
			return {'x' : int(xs), 'y': y}
	return None
def displace(speed, rect, srect):
	"""displace rect moving at given speed out of static rect"""
	
	# replace center of rect on a rectangle of size sum of sizes
	# of rect and srect and centered on srect
	# check intersections with two possible segments
	candidates = []
	invert_x = False
	invert_y = False
	if speed['x'] > 0:
		t = pvVertical(rect.center(),
			{'x' : -speed['x'], 'y' : -speed['y']},
			srect.center()['x'] - srect.w/2 - rect.w/2,
			srect.center()['y'] - srect.h/2 - rect.h/2,
			srect.center()['y'] + srect.h/2 + rect.h/2)
		if t is not None:
			candidates.append(t)
			invert_x = True
	elif speed['x'] < 0:
		t = pvVertical(rect.center(),
			{'x' : -speed['x'], 'y' : -speed['y']},
			srect.center()['x'] + srect.w/2 + rect.w/2,
			srect.center()['y'] - srect.h/2 - rect.h/2,
			srect.center()['y'] + srect.h/2 + rect.h/2)
		if t is not None:
			candidates.append(t)
			invert_x = True
	if speed['y'] > 0:
		t = pvHorizontal(rect.center(),
			{'x' : -speed['x'], 'y' : -speed['y']},
			srect.center()['y'] - srect.h/2 - rect.h/2,
			srect.center()['x'] - srect.w/2 - rect.w/2,
			srect.center()['x'] + srect.w/2 + rect.w/2)
		if t is not None:
			candidates.append(t)
			invert_y = True
	elif speed['y'] < 0:
		t = pvHorizontal(rect.center(),
			{'x' : -speed['x'], 'y' : -speed['y']},
			srect.center()['y'] + srect.h/2 + rect.h/2,
			srect.center()['x'] - srect.w/2 - rect.w/2,
			srect.center()['x'] + srect.w/2 + rect.w/2)
		if t is not None:
			candidates.append(t)
			invert_y = True
	if len(candidates) == 0:
		print 'SIZE ' + str(len(candidates)) + ' ERROR'
		print candidates
		return
	if invert_x:
		speed['x'] = -speed['x']
	if invert_y:
		speed['y'] = -speed['y']
	return candidates[0]['x']-rect.w/2, candidates[0]['y']-rect.h/2

def displaceBallBrick(fn):
	"""displace ball out of collision"""
	def wrapper(self):
		ret = fn(self)
		# side effect: displace ball if collision occurs
		if ret !=None:
			rect = getBrickRect(ret)
			self.ballRect.x, self.ballRect.y = displace(self.ballSpeed, self.ballRect, rect)
		return ret
	return wrapper

class CollisionHandler:

	def __init__(self):
		pass

	def loadState(self, bricks, balls, paddles):
		# TODO make sure grid loading works
		self.gridX = bricks.brickNbByRow
		self.gridY = bricks.rowNb
		self.grid = [None] * self.gridX * self.gridY

		for b in bricks.bricks:
			coordX = b.posX / BRICK_WIDTH
			coordY = b.posY / BRICK_HEIGHT
			self.grid[coordX + self.gridX * coordY] = b
		self.usablesRect = [Rect(u.posX, u.posY, u.width, u.height) for u in bricks.usables if u.isFalling]

		self.ballsRect = [Rect(b.posX-b.radius, b.posY-b.radius, b.radius*2, b.radius*2) for b in balls]
		self.ballsSpeed = [{'x' : b.dX, 'y' : b.dY} for b in balls] 
		self.ballsIsCurving = [b.isCurving for b in balls]
		self.ballsCurve = [b.curve for b in balls]

		self.paddlesRect = [Rect(p.posX, p.posY, p.width, p.height) for p in paddles]
		self.paddlesSpeed = [{'x' : p.dX, 'y' : p.dY} for p in paddles] 
		
	
	def saveState(self, bricks, balls, paddles):

		for i in range(len(balls)):
			balls[i].posX = self.ballsRect[i].x+balls[i].radius
			balls[i].posY = self.ballsRect[i].y+balls[i].radius
			balls[i].dX = self.ballsSpeed[i]['x']
			balls[i].dY = self.ballsSpeed[i]['y']
			balls[i].isCurving = self.ballIsCurving #TODO this might be wrong with N balls
			balls[i].curve = self.ballCurve

		for i in range(len(paddles)):
			paddles[i].posX = self.paddlesRect[i].x
			paddles[i].posY = self.paddlesRect[i].y
			paddles[i].dX = self.paddlesSpeed[i]['x']
			paddles[i].dY = self.paddlesSpeed[i]['y']


	@displaceBallBrick
	def ballBrickCollision(self):
		"""Return hit brick or None
		Displaces ball and inverts ball speed
		GameState should then wear off returned brick"""
		# get 4 potential  "brick coordinates"
		coordX1 = int(self.ballRect.x) / BRICK_WIDTH
		coordX2 = (int(self.ballRect.x) + self.ballRect.w) / BRICK_WIDTH

		coordY1 = int(self.ballRect.y) / BRICK_HEIGHT
		coordY2 = (int(self.ballRect.y) + self.ballRect.h) / BRICK_HEIGHT

		# remove duplicates
		brickList = list(set([(X,Y) 
			for X in range(coordX1, coordX2+1) 
			for Y in range(coordY1, coordY2+1)]))
		
		# keep only bricks that exist in the grid
		brickList = [b for b in brickList 
						if b[0] + b[1] * self.gridX < len(self.grid)
						and b[0] >= 0 and b[1] >= 0
						and b[0] < NB_BRICK_BY_ROW_MAX
						and self.grid[b[0] + b[1] * self.gridX] is not None]
		
		# sort bricks by distance
		# (actually, distance squared to save on computation time)
		brickList.sort(lambda a, b:
			int(
		 	d2(a[0] * BRICK_WIDTH + BRICK_WIDTH / 2,
		 		a[1] * BRICK_HEIGHT + BRICK_HEIGHT / 2,
		 		self.ballRect.x + BALL_RADIUS,
		 		self.ballRect.y + BALL_RADIUS) -
		 	d2(b[0] * BRICK_WIDTH + BRICK_WIDTH / 2,
		 		b[1] * BRICK_HEIGHT + BRICK_HEIGHT / 2,
		 		self.ballRect.x + BALL_RADIUS,
		 		self.ballRect.y + BALL_RADIUS)))

		# closest brick rect, or None if no collision
		if len(brickList) > 0:
			self.ballIsCurving = None
			self.ballCurve = 0
		return brickList[0] if len(brickList) > 0 else None

	def ballPaddleCollision(self):
		"""Bouncing ball off paddle"""
		if Rect.collision(self.ballRect, self.paddleRect):
			# Displace ball
			self.ballRect.y = self.paddleRect.y - self.ballRect.h



			mag = sqrt(self.ballSpeed['x'] * self.ballSpeed['x'] + self.ballSpeed['y'] * self.ballSpeed['y'])
			
			# Add or substract pad speed
			mag += -(BALL_FACTOR * self.paddleSpeed['y'])

			mag *= PADDLE_FACTOR
			if mag > BALL_SPEED_MAX:
				mag = BALL_SPEED_MAX
			elif mag < BALL_SPEED_MIN:
				mag = BALL_SPEED_MIN

			# Ball x and y speed
			theta = (self.ballRect.center()['x'] - self.paddleRect.center()['x'])*((pi/2.5)/(self.paddleRect.w/2+BALL_RADIUS))
			
			# Apply parabolic angular profile
			#theta = theta**3 * (3.0/2)**(1.0/3)

			self.ballSpeed['x'] =  mag * sin(theta)
			self.ballSpeed['y'] =  mag * cos(theta)

			# Add curvature
			factor = abs((self.ballRect.center()['x'] - self.paddleRect.center()['x'])/(self.paddleRect.w/2+BALL_RADIUS))
			factor *= abs(self.paddleSpeed['x'])/PADDLE_H_SPEED['INIT']
			if self.paddleSpeed['x'] > 0:
				if (self.ballRect.center()['x'] - self.paddleRect.center()['x']) > 0:
					#print "curvature y CASE 1"
					self.ballIsCurving = 'Y'
					self.ballCurve = - BALL_CURVE_FACTOR * factor
				elif (self.ballRect.center()['x'] - self.paddleRect.center()['x']) < 0:
					#print "curvature x CASE 3"
					self.ballIsCurving = 'X'
					self.ballCurve = - BALL_CURVE_FACTOR * factor
			elif self.paddleSpeed['x'] < 0:
				if (self.ballRect.center()['x'] - self.paddleRect.center()['x']) > 0:
					#print "curvature x CASE 4"
					self.ballIsCurving = 'X'
					self.ballCurve = BALL_CURVE_FACTOR * factor
				elif (self.ballRect.center()['x'] - self.paddleRect.center()['x']) < 0:
					#print "curvature y CASE 2"
					self.ballIsCurving = 'Y'
					self.ballCurve = - BALL_CURVE_FACTOR * factor

			# Invert speed y
			ysign = 1 if self.ballSpeed['y'] >=0 else -1
			self.ballSpeed['y'] = (-ysign) * self.ballSpeed['y']

			return True

	def ballWallCollision(self):
		"""Bouncing ball off walls (top, left and right)"""
		ret = False
		if self.ballRect.x < 0:
			self.ballRect.x = 0
			self.ballSpeed['x'] = -self.ballSpeed['x']
			ret = True
		elif self.ballRect.x > GAME_WINDOW_WIDTH-self.ballRect.w:
			self.ballRect.x = GAME_WINDOW_WIDTH-self.ballRect.w
			self.ballSpeed['x'] = -self.ballSpeed['x']
			ret = True

		if self.ballRect.y < 0:
			self.ballRect.y = 0
			self.ballSpeed['y'] = -self.ballSpeed['y']
			ret = True

		if ret:
			self.ballIsCurving = None
			self.ballCurve = 0
		return ret

	def ballGroundCollision(self):
		"""Returns True if loss of life should happen"""
		if self.ballRect.y > GAME_WINDOW_HEIGHT - self.ballRect.h:
			self.ballIsCurving = None
			self.ballCurve = 0
			return True
		return False

	def paddleWallCollision(self):
		if self.paddleRect.x < 0:
			self.paddleRect.x = 0
		elif self.paddleRect.x > GAME_WINDOW_WIDTH-self.paddleRect.w:
			self.paddleRect.x = GAME_WINDOW_WIDTH-self.paddleRect.w

		if self.paddleRect.y < 0:
			self.paddleRect.y = 0
		elif self.paddleRect.y > PAD_BOTTOM_LIMIT-self.paddleRect.h:
			self.paddleRect.y = PAD_BOTTOM_LIMIT-self.paddleRect.h

	def paddleUsableCollision(self):
		"""Returns usable index if usable effect should be enabled"""
		for i in range(len(self.usablesRect)):
			if Rect.collision(self.usablesRect[i], self.paddleRect):
				return i
		return None

	def checkAllCollisions(self, activePad=-1):
		"""Returns hit brick (or None), and whether the ball hit the ground"""
		bkHit, bLost, uEffects, ballWall = [],[],[],False
		hitPad = False

		for i in range(len(self.ballsRect)):
			self.ballRect = self.ballsRect[i]
			self.ballSpeed = self.ballsSpeed[i]
			self.ballCurve = self.ballsCurve[i]
			self.ballIsCurving = self.ballsIsCurving[i]

			bkHit.append(self.ballBrickCollision()) # displace + speed inverted
			bLost.append(self.ballGroundCollision()) # no side effect
			if self.ballWallCollision(): # displace + speed inverted 
				ballWall = True
				
		for j in range(len(self.paddlesRect)): 
			self.paddleRect = self.paddlesRect[j]
			self.paddleSpeed = self.paddlesSpeed[j]

			# Ball / pad collision: on active pad only
			if activePad==-1 or (activePad > -1 and j==activePad):
				for i in range(len(self.ballsRect)):
					self.ballRect = self.ballsRect[i]
					self.ballSpeed = self.ballsSpeed[i]
					
					hitPad = self.ballPaddleCollision() # displace + speed inverted/fine-tuned
					#self.ballCurve = self.ballsCurve[i]
					#self.ballIsCurving = self.ballsIsCurving[i]
			self.paddleWallCollision()

			# Usable applied only if not already applied on another pad
			uIndex = self.paddleUsableCollision()
			if not uIndex in [u['uIndex'] for u in uEffects]:
				uEffects.append({'uIndex':uIndex,'padIndex':j})

		#TODO handle brick hit here and only return end of game condition?
		return bkHit, bLost[0], uEffects, hitPad, ballWall


# TODO
# BUG - Usable object collide with more than one pad => apply to the 1st pad of the list (potential synchronization by the master)
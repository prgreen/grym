from brick import Brick
from usable import Usable
from gameObject import GameObject

from constants import(BRICK_WIDTH,
	BRICK_HEIGHT,
	BRICK_TYPE,
	NB_ROW_MAX,
	NB_BRICK_BY_ROW_MAX,
	SCORE_BONUS_MIN,
	SCORE_CHAIN_BONUS,
	BG_COLOR,
	LVL_DIR,
	DEFAULT_TIME)

# Safe eval
from ast import literal_eval
from collections import OrderedDict
import hashlib

# BEWARE: this class is also used by the level editor.
# Don't break compatibility !
class BrickGrid(GameObject):

	LVL_UUID = 0

	def __init__(self):

		self.bricks = []
		self.usables = []

		self.lvlName = "Unnamed"
		self.lvlAuthor = "Anonymous"
		self.bgColor = BG_COLOR
		self.brickNbByRow = 9
		self.rowNb = 9
		self.refTime = ""

	def loadMapFromFile(self, filename):

		# Open map file
		f = open(filename, 'r')
		lines = f.read()
		self.hashsum = hashlib.md5()
		self.hashsum.update(filename)
		self.hashsum.update(lines)

		# Read meta data
		metadata = dict((key,value) for key,value in (line[1:].split('=') for line in lines.split('\n') if line.startswith('#')))

		self.bgColor = [int(c) for c in metadata['BG_COLOR'].split(',')] if 'BG_COLOR' in metadata else BG_COLOR
		self.lvlName = metadata['NAME'] if 'NAME' in metadata else ''
		self.lvlAuthor = metadata['AUTHOR'] if 'AUTHOR' in metadata else ''
		self.refTime = OrderedDict(sorted(literal_eval(metadata['TIME']).iteritems(), key=lambda t:t[1])) if 'TIME' in metadata else {}
		self.lvlId = BrickGrid.LVL_UUID
		BrickGrid.LVL_UUID += 1

		# Read bricks / usables map
		i=0
		mapLines = [line for line in lines.split('\n') if line and not line.startswith('#')]
		self.brickNbByRow = min(NB_BRICK_BY_ROW_MAX, int(metadata['WIDTH']))
		self.rowNb = min(NB_ROW_MAX, len(mapLines))

		for line in mapLines[:self.rowNb]:
			for val in line.split(',')[:self.brickNbByRow]:
				if val:
					# Brick => units digit
					bType = int(val)%10
					if bType > 0:
						posX = BRICK_WIDTH*(i%self.brickNbByRow)
						posY = BRICK_HEIGHT*(i/self.brickNbByRow)
						self.bricks.append( Brick(index=i, posX=posX, posY=posY, bType=bType) )

						# Usable => tens digit
						uType = int(val)/10
						if uType > 0:
							posX += BRICK_WIDTH/2
							self.usables.append( Usable(bIndex=i, posX=posX, posY=posY, uType=uType) )
				i+=1

		# Close map file
		f.close()

	def makeMeta(self, key, value):
		if str(value) != '':
			return '#'+key+'='+str(value)+'\n'
		return ''

	def saveMapToFile(self, filename):
		# Open map file
		f = open(filename, 'w')

		# metadata
		f.write(self.makeMeta('NAME', self.lvlName))
		f.write(self.makeMeta('AUTHOR', self.lvlAuthor))
		f.write(self.makeMeta('BG_COLOR', str(self.bgColor)[1:-1]))
		f.write(self.makeMeta('WIDTH', self.brickNbByRow))
		f.write(self.makeMeta('HEIGHT', self.rowNb))
		f.write(self.makeMeta('TIME', self.refTime))
		f.write('\n\n')

		# bricks and usables
		lvl = ['00'] * self.brickNbByRow * self.rowNb

		for b in self.bricks:
			coordX = int(b.posX / BRICK_WIDTH)
			coordY = int(b.posY / BRICK_HEIGHT)

			index = coordX + coordY * self.brickNbByRow

			lvl[index] = '0'+str(b.bType)

		for u in self.usables:
			coordX = int((u.posX + u.width/2 - BRICK_WIDTH/2) / BRICK_WIDTH)
			coordY = int(u.posY / BRICK_HEIGHT)

			index = coordX + coordY * self.brickNbByRow

			lvl[index] = str(u.uType)+lvl[index][1:]

		lvlList = list(",".join(lvl))
		# every end of line, replace "," with "\n"
		for i in range(self.rowNb-1):
			lvlList[(i+1)*self.brickNbByRow*3-1] = "\n"

		f.write("".join(lvlList))

		f.close()
	def addBrick(self, bType, x, y):
		# TODO real index
		# Remove existing
		#print "bricks "+str(len(self.bricks))
		self.bricks = [ b for b in self.bricks if (b.posX != x*BRICK_WIDTH or b.posY!=y*BRICK_HEIGHT)]
		#print "bricks "+str(len(self.bricks))
		#print "usables "+str(len(self.usables))
		self.usables = [ u for u in self.usables if (u.posX != x*BRICK_WIDTH+BRICK_WIDTH/2-u.width/2 or u.posY!=y*BRICK_HEIGHT)]
		#print "usables "+str(len(self.usables))
		if bType > 0:
			self.bricks.append(Brick(index=-1, posX=x*BRICK_WIDTH, posY=y*BRICK_HEIGHT, bType=bType))

	def addUsable(self, uType, x, y):
		# TODO real index
		
		self.usables.append(Usable(bIndex=-1, posX=x*BRICK_WIDTH+BRICK_WIDTH/2, posY=y*BRICK_HEIGHT, uType=uType))

	def hitBrick(self, brickHit, chainBonus):
		""" Finds and updates state of hit brick """
		score = 0
		remBricks = [1]

		for b in list(self.bricks): #iterate on copy
			if b.posX / BRICK_WIDTH == brickHit[0] and b.posY / BRICK_HEIGHT == brickHit[1]:
				res, score = b.hit()

				# Update chain bonus
				if b.bType != BRICK_TYPE['STEEL']:
					chainBonus = chainBonus+1 if chainBonus < len(SCORE_CHAIN_BONUS)-1 else chainBonus
				else:
					chainBonus = 0

				# Remove brick if no more resistance
				if res == 0:
					# Enable matching usables
					[u.setFalling() for u in self.usables if u.bIndex == b.bIndex]
					# Remove brick
					self.bricks.remove(b)
					# Count remaining breakable bricks
					remBricks = [brk for brk in self.bricks if brk.bType != BRICK_TYPE['STEEL']]

		return score, chainBonus, len(remBricks)


	def getUsableEffect(self, index):
		""" Returns falling usable effect / object and removes it from list """
		i=0
		for u in list(self.usables):
			if u.isFalling:
				if index == i:
					self.usables.remove(u)
					return u.getEffect()
				i+=1


	def update(self):
		for b in self.bricks:
			b.update()

		for u in self.usables:
			if u.isFalling:
				u.update()

	def getType(self, brk):
		for b in list(self.bricks): #iterate on copy
			if b.posX / BRICK_WIDTH == brk[0] and b.posY / BRICK_HEIGHT == brk[1]:
				return b.bType
	def getBrk(self, brk):
		for b in self.bricks:
			if b.posX / BRICK_WIDTH == brk[0] and b.posY / BRICK_HEIGHT == brk[1]:
				return b
		return None
	def isNearExplosionSource(self, bx, by, sx, sy, depth):
		if bx == sx and by == sy:
			return False
		if bx == sx:
			if abs(by - sy) <= depth:
				return True
		elif by == sy:
			if abs(bx - sx) <= depth:
				return True
		return False
	def explode(self, brk, depth=1, listExp=[], firstCall=True, direction="UP"):
		retList=[brk]
		#print "boom ", str(brk[0]), str(brk[1])
		brick = self.getBrk(brk)
		if brick != None:
			if brick.bType == BRICK_TYPE['NITRO']:
				listExploded = [b for b in self.bricks if self.isNearExplosionSource(b.posX / BRICK_WIDTH, b.posY / BRICK_HEIGHT, brk[0], brk[1], depth) and b not in listExp]
				for b in listExploded:
					retList += self.explode((b.posX/BRICK_WIDTH,b.posY/BRICK_HEIGHT), depth+1, [brick]+listExp+listExploded, False, self.getDirection(brick.posX, brick.posY, brick.width, brick.height, b.posX, b.posY))
					#self.hitBrick((b.posX/BRICK_WIDTH,b.posY/BRICK_HEIGHT), 0)
			elif brick.bType == BRICK_TYPE['MASSIVE']:
				#print direction
				depth=1
				listExploded = self.getBrickLine(brk, direction)
				listExploded = [b for b in listExploded if b not in listExp]
				for b in listExploded:
					retList += self.explode((b.posX/BRICK_WIDTH,b.posY/BRICK_HEIGHT), depth, [brick]+listExp+listExploded, False, direction)
			if not firstCall:
				self.hitBrick(brk, 0)
			return retList
		return []
	def getNextBrickDirection(self, brk, direction):
		if direction == "UP":
			return self.getBrk((brk[0], brk[1]-1))
		if direction == "DOWN":
			return self.getBrk((brk[0], brk[1]+1))
		if direction == "LEFT":
			return self.getBrk((brk[0]-1, brk[1]))
		if direction == "RIGHT":
			return self.getBrk((brk[0]+1, brk[1]))
		return None
	def getBrickLine(self, brk, direction):
		retList = []
		temp = self.getNextBrickDirection(brk, direction)
		while temp is not None:
			if temp.bType != BRICK_TYPE['STEEL']:
				retList.append(temp)
				temp = self.getNextBrickDirection((temp.posX/BRICK_WIDTH,temp.posY/BRICK_HEIGHT), direction)
			else:
				break 
			
		return retList
	def getDirection(self, x0, y0, w0, h0, x1, y1):
		if y1 < y0 - h0/2:
			return "UP"
		if y1 > y0 + h0/2:
			return "DOWN"
		if x1 > x0 + w0/2:
			return "RIGHT"
		if x1 < x0 - w0/2:
			return "LEFT"
		return "UP"
	def draw(self, screen):
		for b in self.bricks:
			b.draw(screen)

		for u in self.usables:
			if u.isFalling:
				u.draw(screen)

	def drawStatic(self, screen, withUsables=True):
		""" Used in level editor to show both bricks and usables """
		for b in self.bricks:
			b.draw(screen)
		if withUsables:
			for u in self.usables:
				u.draw(screen)
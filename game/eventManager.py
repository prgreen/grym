import pygame
from counter import Counter

class EventManager:

	def __init__(self):

		# Quit
		self.quitEvent = False

		# Space
		self.spacePressed = False
		self.spaceReleased = False

		# Arrows
		self.leftHeld = False
		self.rightHeld = False
		self.upHeld = False
		self.downHeld = False

		self.leftPressed = False
		self.rightPressed = False
		self.upPressed = False
		self.downPressed = False

		self.leftReleased = False
		self.rightReleased = False
		self.upReleased = False
		self.downReleased = False

		# Horizontal boost time counters
		self.hBoostLeft = Counter(200)
		self.hBoostRight = Counter(200)
		self.hBoostLeft.start()
		self.hBoostRight.start()
		self.isBoostingLeft = False
		self.isBoostingRight = False

		# Keys
		self.yPressed = False
		self.nPressed = False
		self.escapePressed = False

	def reset(self):
		# Quit
		self.quitEvent = False

		# Space
		self.spacePressed = False
		self.spaceReleased = False

		# Arrows
		self.leftHeld = False
		self.rightHeld = False
		self.upHeld = False
		self.downHeld = False

		self.leftPressed = False
		self.rightPressed = False
		self.upPressed = False
		self.downPressed = False

		self.leftReleased = False
		self.rightReleased = False
		self.upReleased = False
		self.downReleased = False

		# Keys
		self.yPressed = False
		self.nPressed = False
		self.escapePressed = False

	def update(self):
		""" Update keyboard state """

		# Set all attributes to false
		self.reset()

		# Click / press / release events
		for event in pygame.event.get():

			# Key pressed events
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.spacePressed = True
				elif event.key == pygame.K_y:
					self.yPressed = True
				elif event.key == pygame.K_n:
					self.nPressed = True
				elif event.key == pygame.K_ESCAPE:
					self.escapePressed = True
				elif event.key == pygame.K_LEFT:
					self.leftPressed = True
					if self.hBoostLeft.timeOut():
						pass
					else:
						#print "BOOST left"
						self.isBoostingLeft = True
				elif event.key == pygame.K_RIGHT:
					self.rightPressed = True
					if self.hBoostRight.timeOut():
						pass
					else:
						#print "BOOST right"
						self.isBoostingRight = True
				elif event.key == pygame.K_UP:
					self.upPressed = True
				elif event.key == pygame.K_DOWN:
					self.downPressed = True

			# Key released events
			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					self.leftReleased = True
					self.hBoostLeft.start()
				elif event.key == pygame.K_RIGHT:
					self.rightReleased = True
					self.hBoostRight.start()
				elif event.key == pygame.K_UP:
					self.upReleased = True
				elif event.key == pygame.K_DOWN:
					self.downReleased = True
				elif event.key == pygame.K_SPACE:
					self.spaceReleased = True

			# Quit event
			elif event.type == pygame.QUIT:
				self.quitEvent = True

		# Hold events
		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT]:
			self.leftHeld = True
		if key[pygame.K_RIGHT]:
			self.rightHeld = True
		if key[pygame.K_UP]:
			self.upHeld = True
		if key[pygame.K_DOWN]:
			self.downHeld = True

		# Continue boosting as long as key is held
		if self.isBoostingLeft and self.leftHeld:
			self.isBoostingLeft = True
		else:
			self.isBoostingLeft = False
		if self.isBoostingRight and self.rightHeld:
			self.isBoostingRight = True
		else:
			self.isBoostingRight = False



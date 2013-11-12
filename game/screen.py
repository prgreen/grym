from counter import Counter

from constants import *

import pygame


class Screen:

	def __init__(self, window, color, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, x0=0, y0=0, alpha=-1):
		self.x0 = x0
		self.y0 = y0
		self.width = width
		self.height = height
		self.color = color
		self.prevSurface = None
		self.alpha = alpha

		self.window = window


	def drawBG(self, bgColor=''):

		# Draw self color if stateboard
		if bgColor == '':
			bgColor = self.color
		rect =  (self.x0, self.y0, self.width, self.height)
		# Transparency
		if self.alpha+1>0:
			# Get previous surface
			if self.prevSurface is None:
				self.prevSurface = self.window.subsurface(rect).copy()
			self.window.blit(self.prevSurface, (self.x0, self.y0))

			# Paste transparent surface
			surface = pygame.Surface((self.width, self.height))
			surface.fill(bgColor)
			surface.set_alpha(self.alpha)
			self.window.blit(surface, (self.x0, self.y0))
		else:
			pygame.draw.rect(self.window, bgColor, (self.x0, self.y0, self.width, self.height))


	def drawObject(self, obj, shape, border=True, alpha=-1):
		""" Draws shape on screen """
		if shape == SHAPE['CIRCLE']:
			# Transparency
			if alpha+1>0:
				surface = pygame.Surface((obj.radius*2,obj.radius*2))
				pos = (0, 0)
			else:
				surface = self.window
				pos = (self.x0+int(obj.posX), self.y0+int(obj.posY))

			# Inside
			pygame.draw.circle(surface, obj.color, pos, obj.radius)
			# Border
			if border:
				pygame.draw.circle(surface, DEFAULT_COLOR, pos, obj.radius, DEFAULT_BORDER_WIDTH)

		elif shape == SHAPE['RECT']:
			# Transparency
			if alpha+1>0:
				surface = pygame.Surface((obj.width,obj.height))
				rect = (0, 0, obj.width, obj.height)
			else:
				surface = self.window
				rect = (self.x0+int(obj.posX), self.y0+int(obj.posY), obj.width, obj.height)

			# Inside
			pygame.draw.rect(surface, obj.color, rect)
			# Border
			if border:
				pygame.draw.rect(surface, DEFAULT_COLOR, rect, DEFAULT_BORDER_WIDTH)

		# If transparency => stick transparent surface on main window
		if alpha+1>0:
			surface.set_alpha(alpha)
			self.window.blit(surface, (self.x0+obj.posX, self.y0+obj.posY))


	def drawText(self, text, size, posX=0, posY=0, refRect=None, style=GLOBAL_FONT, color=DEFAULT_COLOR, bold=0, alignH=TEXT_ALIGN['H']['LEFT'], alignV=TEXT_ALIGN['V']['TOP'], border=False, blink=False):

		# If reference Rect => adjust posX posY
		if refRect is not None:
			width = refRect.width
			height = refRect.height
			refX0 = refRect.posX if refRect.width%2==1 else refRect.posX-1
			refY0 = refRect.posY
		else:
			refX0 = 0
			refY0 = 0
			width = self.width
			height = self.height

		font = pygame.font.SysFont(name=style, size=size, bold=bold)
		#font = pygame.font.Font('data/fonts/gamefont.ttf', size)
		lbl = font.render(text, True, color)
		""" Text align - BEGIN """
		fontRect = lbl.get_rect()

		# Horizontal text align: CENTER => auto posX
		if alignH == TEXT_ALIGN['H']['CENTER']:
			fontRect.centerx = pygame.Rect(refX0+self.x0, refY0+self.y0+posY, width, height).centerx
		elif alignH == TEXT_ALIGN['H']['RIGHT']:
			fontRect.right = pygame.Rect(refX0+self.x0-posX, refY0+self.y0+posY, width, height).right
		else:
			fontRect.x = pygame.Rect(refX0+self.x0+posX, refY0+self.y0+posY, width, height).x

		# Vertical text align: MIDDLE => auto posY
		if alignV == TEXT_ALIGN['V']['MIDDLE']:
			fontRect.centery = pygame.Rect(refX0+self.x0+posX, refY0+self.y0, width, height).centery
		elif alignV == TEXT_ALIGN['V']['BOTTOM']:
			fontRect.bottom = pygame.Rect(refX0+self.x0+posX, refY0+self.y0-posY, width, height).bottom
		else:
			fontRect.y = pygame.Rect(refX0+self.x0+posX, refY0+self.y0+posY, width, height).y
		""" Text align - END """


		# Blink
		if not blink or (blink and (Counter.FRAME_CNT/(FPS/2)) % 2 == 0):
			# Border / hollow
			if border:
				borderFont = pygame.font.SysFont(name=style, size=size, bold=bold)
				lblBorder = borderFont.render(text, True, (0,0,0))
				borderFontRect = lblBorder.get_rect()
				borderFontRect.centerx = fontRect.centerx-1
				borderFontRect.centery = fontRect.centery+1
				self.window.blit(lblBorder, borderFontRect)

			# Print text
			self.window.blit(lbl, fontRect)

		return refY0 + fontRect.bottom - self.y0


	def drawSprite(self, surface, posX=0, posY=0):
		self.window.blit(surface, (self.x0+posX, self.y0+posY))

from pgu import gui
import pygame
from pygame.constants import *
from game.constants import *
from game.brickGrid import BrickGrid
from game.mainBoard import MainBoard

from ast import literal_eval

FPS=60

class StateManager:
	"""Manage a dictionary of states"""
	def __init__(self, states):
		self.states = states
		for k,v in self.states.iteritems():
			v.manager = self
		self.active = self.states["MENU"]

		self.level = BrickGrid()

		self.done = False

	def init(self):
		pygame.init()

		self.screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.SWSURFACE)
		pygame.display.set_caption("Grymark Level Editor")

	def exit(self):
		pygame.quit() 

	def update(self):
		self.active.update(pygame.event.get())

	def draw(self):
		self.active.draw(self.screen)

	def changeState(self, newState):
		self.active.onLeave()
		self.active = self.states[newState]
		self.active.onEnter()

class AbstractState:
	"""Abstract class for states"""
	def onEnter(self):
		pass
	def onLeave(self):
		pass
	def update(self, events):
		pass
	def draw(self, screen):
		pass

class MenuState(AbstractState):
	"""Menu to open/save level files and adjust level settings"""
	def __init__(self):
		self.app = gui.App()
		self.app.connect(gui.QUIT, self.app.quit, None)

		self.fileDialog = gui.FileDialog("Open Level file (.txt)", "Ok", "dialog", LVL_DIR)
		self.fileDialog.connect(gui.CHANGE, self.updateFilename)

		self.f = gui.Form()
		self.t = gui.Table(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

		self.t.tr()
		self.newButton = gui.Button('Create New Level')
		self.newButton.connect(gui.CLICK, self.createLevel)
		self.t.td(self.newButton, colspan=4)
		
		self.t.tr()
		self.openButton = gui.Button('Open Level File')
		self.openButton.connect(gui.CLICK, self.openFile)
		self.t.td(self.openButton, colspan=4)


		self.t.tr()
		self.saveButton = gui.Button('Save All Changes')
		self.saveButton.connect(gui.CLICK, self.saveFile)
		self.t.td(self.saveButton, colspan=4)

		self.t.tr()
		self.filenameLabel = gui.Label('Filename')
		self.t.td(self.filenameLabel)
		self.filenameInput = gui.Input(size=24, name="Filename")
		self.t.td(self.filenameInput, colspan=3)

		self.t.tr()
		self.levelVariablesLabel = gui.Label('LEVEL VARIABLES')
		self.t.td(self.levelVariablesLabel, colspan=4)

		self.t.tr()
		self.warningLabel = gui.Label('Don\'t forget to save your changes !')
		self.t.td(self.warningLabel, colspan=4)

		self.t.tr()
		self.nameLabel = gui.Label('NAME')
		self.t.td(self.nameLabel)
		self.nameInput = gui.Input(size=16, name="NAME")
		self.t.td(self.nameInput, colspan=3)

		self.t.tr()
		self.authorLabel = gui.Label('AUTHOR')
		self.t.td(self.authorLabel)
		self.authorInput = gui.Input(size=16, name="AUTHOR")
		self.t.td(self.authorInput, colspan=3)

		self.t.tr()
		self.bgcolorLabel = gui.Label('BG_COLOR')
		self.t.td(self.bgcolorLabel)
		self.bgcolorInput = gui.Input(size=16, name="BGCOLOR")
		self.t.td(self.bgcolorInput, colspan=3)

		self.t.tr()
		self.widthLabel = gui.Label('WIDTH')
		self.t.td(self.widthLabel)
		self.widthInput = gui.Input(size=16, name="WIDTH")
		self.t.td(self.widthInput, colspan=3)

		self.t.tr()
		self.heightLabel = gui.Label('HEIGHT')
		self.t.td(self.heightLabel)
		self.heightInput = gui.Input(size=16, name="HEIGHT")
		self.t.td(self.heightInput, colspan=3)

		self.t.tr()
		self.timeLabel = gui.Label('TIME')
		self.t.td(self.timeLabel)
		self.timeInput = gui.Input(size=16, name="TIME")
		self.t.td(self.timeInput, colspan=3)

		self.t.tr()
		self.editButton = gui.Button('EDIT LEVEL')
		self.editButton.connect(gui.CLICK, self.editLevel)
		self.t.td(self.editButton, colspan=4)
			
		self.t.tr()
		self.playButton = gui.Button('PLAY LEVEL')
		self.t.td(self.playButton, colspan=4)

		self.app.init(self.t)

	def createLevel(self):
		self.clearAll()
		self.filenameInput.value = LVL_DIR+"custom.txt"
		self.manager.level = BrickGrid()

		self.nameInput.value = self.manager.level.lvlName
		self.authorInput.value = self.manager.level.lvlAuthor
		self.bgcolorInput.value = str(self.manager.level.bgColor)[1:-1]
		self.widthInput.value = str(self.manager.level.brickNbByRow)
		self.heightInput.value = str(self.manager.level.rowNb)
		self.timeInput.value = str(self.manager.level.refTime)



	def clearAll(self):
		self.nameInput.value = ""
		self.authorInput.value = ""
		self.bgcolorInput.value = ""
		self.widthInput.value = ""
		self.heightInput.value = ""
		self.timeInput.value = ""

	def openFile(self):
		self.fileDialog.open()

	def saveFile(self):
		# update
		self.manager.level.lvlName = self.nameInput.value
		self.manager.level.lvlAuthor = self.authorInput.value
		self.manager.level.bgColor = literal_eval(self.bgcolorInput.value)
		self.manager.level.brickNbByRow = int(self.widthInput.value)
		self.manager.level.rowNb = int(self.heightInput.value)
		self.manager.level.refTime = self.timeInput.value

		# save 
		self.manager.level.saveMapToFile(self.filenameInput.value)

	def updateFilename(self):
		self.filenameInput.value = self.fileDialog.value

		self.loadLevelVariables(self.filenameInput.value)

		self.manager.level = BrickGrid()
		self.manager.level.loadMapFromFile(self.filenameInput.value)

	def loadLevelVariables(self, filename):
		# Open map file
		f = open(filename, 'r')
		lines = f.read()

		# Read meta data
		metadata = dict((key,value) for key,value in (line[1:].split('=') for line in lines.split('\n') if line.startswith('#')))
		
		self.clearAll()
		try:
			self.nameInput.value = metadata['NAME']
			self.authorInput.value = metadata['AUTHOR']
			self.bgcolorInput.value = metadata['BG_COLOR']
			self.widthInput.value = metadata['WIDTH']
			self.heightInput.value = metadata['HEIGHT']
			self.timeInput.value = metadata['TIME']
		except KeyError:
			pass

		f.close()

	def editLevel(self):
		self.manager.changeState("EDIT")

	def onEnter(self):
		pass
		#self.__init__()
	def onLeave(self):
		pass
	def update(self, events):
		for e in events:
			if e.type is QUIT:
				self.manager.done = True
			elif e.type is KEYDOWN and e.key == K_ESCAPE: 
					self.manager.done = True
			else:
				self.app.event(e)
	def draw(self, screen):
		screen.fill((200,200,200))
		self.app.paint()    
		pygame.display.flip()


class HelpState(AbstractState):
	"""Help sheet with available commands"""
	def __init__(self):
		self.app = gui.App()
		self.app.connect(gui.QUIT, self.app.quit, None)

		self.hello = gui.Button("This is the help")
		self.hello.connect(gui.CLICK, self.print_help)
		self.app.init(self.hello)
	def print_help(self):
		print "help"
	def onEnter(self):
		pass
	def onLeave(self):
		pass
	def update(self, events):
		for e in events:
			if e.type is QUIT:
				self.manager.done = True
			elif e.type is KEYDOWN:
				if e.key == K_ESCAPE: 
					self.manager.done = True
				elif e.unicode == 'e':
					self.manager.changeState("EDIT")
				elif e.unicode == 'm':
					self.manager.changeState("MENU")
			else:
				self.app.event(e)
	def draw(self, screen):
		screen.fill((0,0,0))
		self.app.paint()    
		pygame.display.flip()

class EditState(AbstractState):
	"""Edit level bricks/usables with keyboard/mouse commands"""
	def __init__(self):
		self.selBrick = 0
		self.selUsable = 0
	def onEnter(self):
		self.screen = MainBoard(self.manager.screen)
	def onLeave(self):
		pass
	def update(self, events):
		for e in events:
			if e.type is QUIT:
				self.manager.done = True
			elif e.type is KEYDOWN:	
				if e.key == K_ESCAPE: 
					self.manager.done = True
				elif e.key == K_UP:
					if self.selBrick < len(BRICK_TYPE):
						self.selBrick += 1
				elif e.key == K_DOWN:
					if self.selBrick > 0:
						self.selBrick -= 1
				elif e.key == K_LEFT:
					if self.selUsable > 0:
						self.selUsable -= 1
				elif e.key == K_RIGHT:
					if self.selUsable < len(USABLE_TYPE):
						self.selUsable += 1
				elif e.unicode == 'h':
					self.manager.changeState("HELP")
				elif e.unicode == 'm':
					self.manager.changeState("MENU")

		if pygame.mouse.get_pressed()[0]:
			mouseX, mouseY = pygame.mouse.get_pos()
			coordX = int((mouseX-GAME_WINDOW_X0) / BRICK_WIDTH)
			coordY = int(mouseY / BRICK_HEIGHT)
			if coordX >= 0 and coordY >= 0 and coordX < self.manager.level.brickNbByRow and coordY < self.manager.level.rowNb:
				#place brick and usable
				self.addBrick(self.selBrick, coordX, coordY)
				if self.selBrick > 0:
					self.addUsable(self.selUsable, coordX, coordY)
	def addBrick(self, bType, x, y):
		self.manager.level.addBrick(bType, x, y)
	def addUsable(self, uType, x, y):
		if uType > 0:
			self.manager.level.addUsable(uType, x, y)
	def draw(self, screen):
		screen.fill((0,0,0))

		# GAMEBOARD
		self.screen.screens['GAMEBOARD'].drawBG(self.manager.level.bgColor)
		self.manager.level.drawStatic(self.screen.screens['GAMEBOARD'])
		
		# STATE BOARD

		self.screen.screens['STATEBOARD'].drawText("Brick: "+str(self.selBrick), 20, color=(255,255,255), posX=5, posY=20)
		self.screen.screens['STATEBOARD'].drawText(BRICK_DESC[self.selBrick], 10, color=(255,255,255), posX=5, posY=60)
		
		self.screen.screens['STATEBOARD'].drawText("Usable: "+str(self.selUsable), 20, color=(255,255,255), posX=5, posY=200)
		self.screen.screens['STATEBOARD'].drawText(USABLE_DESC[self.selUsable], 10, color=(255,255,255), posX=5, posY=240)
		
		mouseX, mouseY = pygame.mouse.get_pos()
		mouseX = int(max(0, (mouseX-GAME_WINDOW_X0) / BRICK_WIDTH))
		mouseY = int(mouseY / BRICK_HEIGHT)
		self.screen.screens['STATEBOARD'].drawText(str(mouseX)+','+str(mouseY), 12, color=(255,255,255), posX=0, posY=WINDOW_HEIGHT-20)


		pygame.display.flip()



if __name__ == '__main__':

	states = {"MENU" : MenuState(),
		      "HELP" : HelpState(),
		      "EDIT" : EditState()}

	editor = StateManager(states)

	editor.init()

	clock = pygame.time.Clock()
	while not editor.done:		
		editor.update()
		editor.draw()
		clock.tick(FPS)

	editor.exit()
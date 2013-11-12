from pgu import gui
import pygame
from pygame.constants import *
from net.client import NetClient
from game.grymark import Grymark
from game.constants import GAME_MODE, WINDOW_WIDTH, WINDOW_HEIGHT, LVL_DIR
import webbrowser
import os

REGISTRATION_URL = "http://grymark.us.to/register"
HOST = '127.0.0.1' #88.191.131.158
PORT = 1789
LISTEN_PORT = 1790

class GuiNetClient(NetClient):
    def __init__(self, host, port, listen_port):
        super(GuiNetClient, self).__init__(host, port, listen_port)

    def resAuth(self, authorized):
        if authorized:
            #print "change screen"
            self.gameList()
            app.init(self.gui.gameList)
            self.gui = self.gui.gameList
        else:
            self.gui.usernameInput.value = ""
            self.gui.passwordInput.value = ""
            self.gui.loginLabel.style.color = (255, 0, 0)
            self.gui.loginLabel.set_text("Unauthorized! Try again")


    def resGameList(self, content, serverMessage):
        self.gui.serverMessage.set_text(serverMessage)
        self.gList = content

        self.gui.list.clear()
        index = 0
        for g in self.gList:
            self.gui.list.add(g, value=index) #TODO add value
            index += 1
        #self.gui.list.add("game1", value=1)
        #self.gui.list.add("game2", value=2)
        self.gui.list.resize()
        self.gui.list.repaint()



class PasswordInput(gui.Input):

    def paint(self,s):
        r = pygame.Rect(0,0,self.rect.w,self.rect.h)
        
        cs = 2 #NOTE: should be in a style
        
        w,h = self.font.size('*' * self.pos)
        x = w-self.vpos
        if x < 0: self.vpos -= -x
        if x+cs > s.get_width(): self.vpos += x+cs-s.get_width()
        
        s.blit(self.font.render('*' * len(self.value), 1, self.style.color),(-self.vpos,0))
        
        if self.container.myfocus is self:
            w,h = self.font.size('*' * self.pos)
            r.x = w-self.vpos
            r.w = cs
            r.h = h
            s.fill(self.style.color,r)

class Login(gui.Table):
    def __init__(self, net, gameList):
        super(Login, self).__init__()
        self.gameList = gameList
        self.net = net
        self.f = gui.Form()

        self.tr()
        self.singlePlayerLabel = gui.Label("Single Player")
        self.td(self.singlePlayerLabel, colspan=2)

        for d in os.listdir(LVL_DIR):
            self.tr()
            temp = gui.Button(d)
            temp.connect(gui.CLICK, self.onSinglePlayer, d)
            self.td(temp, colspan=2)

        self.tr()
        self.td(gui.Spacer(width=0, height=100))

        self.tr()
        self.loginLabel = gui.Label("Multiplayer (login required)")
        self.td(self.loginLabel, colspan=2)

        self.tr()
        self.td(gui.Spacer(width=0, height=10))

        #TODO display server status (online/offline/overloaded)

        self.tr()
        self.usernameInput = gui.Input(size=16, name="username")
        self.td(gui.Label("Username"), align=-1)
        self.td(self.usernameInput, align=-1)

        self.tr()
        self.passwordInput = gui.Password(size=16, name="password")
        self.td(gui.Label("Password"), align=-1)
        self.td(self.passwordInput, align=-1)

        self.tr()
        self.td(gui.Spacer(width=0, height=10))

        self.tr()
        e = gui.Button("Validate")
        e.connect(gui.CLICK, self.onValidate)
        self.td(e, colspan=2)

        self.tr()
        self.td(gui.Spacer(width=0, height=50))

        self.tr()
        self.td(gui.Label("No account yet? Use this button: "), colspan=2)

        self.tr()
        reg = gui.Button("Register new account")
        reg.connect(gui.CLICK, lambda : webbrowser.open(REGISTRATION_URL))
        self.td(reg, colspan=2)

    def onValidate(self):
        d = self.f.results()
        self.net.auth(d['username'], d['password'])
    def onSinglePlayer(self, d):
        Grymark('Hero', GAME_MODE['SINGLE_ADVENTURE'], d)
        #TODO at the end of the game, allow to save hi-score online
        # after login prompt
class GameList(gui.Table):
    def __init__(self, net):
        super(GameList, self).__init__()
        self.net = net
        self.createGameDialog = CreateGameDialog(self.net)

        self.tr()
        self.serverMessage = gui.Label("Waiting for server message...")
        self.td(self.serverMessage, colspan=2)

        self.tr()
        self.list = gui.List(width=150, height=100)
        self.td(self.list, colspan=2)

        self.tr()
        self.joinButton = gui.Button("Join")
        self.joinButton.connect(gui.CLICK, self.joinGame)
        self.createButton = gui.Button("Create")
        self.createButton.connect(gui.CLICK, self.createGameDialog.open, None)   
        self.td(self.joinButton)
        self.td(self.createButton)

        self.tr()
        self.refreshButton = gui.Button("Refresh game list")
        self.refreshButton.connect(gui.CLICK, self.refreshGameList)
        self.td(self.refreshButton, colspan=2)

    def refreshGameList(self):
        self.net.gameList()

    def joinGame(self):
        if self.list.value != None:
            print "JOINING " + str(self.list.value)
            self.net.joinGame(self.net.gList[self.list.value])

class CreateGameDialog(gui.Dialog):
    def __init__(self, net, **params):
        self.net = net
        self.value = gui.Form()

        title = gui.Label("Create Game")
        
        t = gui.Table()

        t.tr()
        t.td(gui.Label("Name"))
        self.nameEdit = gui.Input(name="name")
        t.td(self.nameEdit)

        self.g = gui.Group(name="gameMode", value="CLASSIC")
        t.tr()
        t.td(gui.Label("Classic (co-op)"))
        self.classic = gui.Radio(self.g, "CLASSIC")
        t.td(self.classic)

        t.tr()
        t.td(gui.Label("Alternate"))
        self.alternate = gui.Radio(self.g, "ALTERNATE")
        t.td(self.alternate)

        t.tr()
        t.td(gui.Label("Multi Ball"))
        self.multiball = gui.Radio(self.g, "MULTIBALL")
        t.td(self.multiball)

        self.g.connect(gui.CHANGE, self.changeRadio, self.g)
        
        t.tr()
        self.createButton = gui.Button("Create")
        self.createButton.connect(gui.CLICK,self.createGame)
        t.td(self.createButton)
        ##
        
        self.cancelButton = gui.Button("Cancel")
        self.cancelButton.connect(gui.CLICK,self.close, None)
        t.td(self.cancelButton)
        
        gui.Dialog.__init__(self,title,t)

    def changeRadio(self, g):
        #print "RADIO " + g.value
        self.g.value = g.value
        #print "RADIO " + self.g.value

    def createGame(self):
        gameMode = self.g.value
        d = self.value.results()
        print "CREATE " + d['name'] + " " + gameMode
        #TODO use gameMode option in game creation
        self.net.createGame(d['name'])
        self.close()
        # TODO small delay here? 
        self.net.gameList()

if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.init()

    net = GuiNetClient(HOST, PORT, LISTEN_PORT)
    screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.SWSURFACE)
    pygame.display.set_caption("Grym Lobby")

    app = gui.Desktop()
    app.connect(gui.QUIT, app.quit, None)

    # chaining screens together
    gameList = GameList(net)
    login = Login(net, gameList)


    net.gui = login
    app.init(login)

    FPS=60
    clock = pygame.time.Clock()
    done = False
    while not done:
        for e in pygame.event.get():
            if e.type is QUIT: 
                done = True
            elif e.type is KEYDOWN and e.key == K_ESCAPE: 
                done = True
            else:
                app.event(e)

        # Clear the screen
        net.step()
        screen.fill((0,0,0))

        app.paint()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()    
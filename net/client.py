#!/usr/bin/python
# -*- coding: utf-8 -*-
# Client will:
# - Authenticate itself to the server
# - Retrieve a game list and display it
# - Allow to create (master) OR join (slave) a game
# - Connect with other players behind NATs
# - Send data to other players (and server if game master)
# - Feature a small interactive console-based mode for debugging

from UDP import UDP
import msgpack



class NetClient(UDP):
	def __init__(self, host, port, listen_port):
		super(NetClient, self).__init__(host, port, listen_port)

		self.master = {}
		self.slaves = []

	def sendMaster(self, msg):
		self.s.sendto(msgpack.packb(msg), self.master['addr'])

	def sendSlaves(self, msg):
		for slave in self.slaves:
			self.s.sendto(msgpack.packb(msg), slave['addr'])

	def sendSlave(self, msg, username):
		slave = None
		for s in self.slaves:
			if s['username'] == username:
				slave = s
				break
		if slave:
			self.s.sendto(msgpack.packb(msg), slave['addr'])

	def auth(self, username, password):
		self.request('auth', username=username, password=password)

	def resAuth(self, authorized):
		if authorized:
			print 'AUTH success'
		else:
			print 'AUTH failure'
		self.gameList()

	def gameList(self):
		self.request('gameList')

	def resGameList(self, content, serverMessage):
		GAMELIST = content

		# Console based choice of game
		for i,g in enumerate(GAMELIST):
			print i+1,'. ', g
		print '---'
		chosen_game = int(raw_input('Choose a game or enter 0 to create new game:\n'))
		if chosen_game != 0:
			print 'JOINING ' + GAMELIST[chosen_game-1]
			self.joinGame(GAMELIST[chosen_game-1])
		else:
			print 'CREATE'
			name = raw_input('Enter a game name:\n')
			self.createGame(name)

	def createGame(self, name):
		self.request('createGame', name=name)

	def joinGame(self, name):
		self.request('joinGame', name=name)

	def resConnectToSlave(self, address, username):
		slave = {}
		slave['username'] = username
		slave['addr'] = tuple(address)

		self.slaves.append(slave)

		# send pings until response
		self.sendSlave('ping', username)

	def resConnectToMaster(self, address, username):
		self.master['username'] = username
		self.master['addr'] = tuple(address)
		# send pings until response
		self.sendMaster('ping')

	def step(self):
		self.update()
		while True:
			msg = self.recv()
			if msg != None:
				data, addr = msg
				if addr[0] == self.distant_host and addr[1] == self.distant_port: #TODO gethostbyname
					try:
						if 'arg' in data:
							getattr(self, 'res' + data['cmd'][:1].upper() + data['cmd'][1:])(**data['arg'])
						else:
							getattr(self, 'res' + data['cmd'][:1].upper() + data['cmd'][1:])()
					except Exception, err:
						print data['cmd'] + ' unimplemented or error'
						print err
				else:
					#TODO check that addr in list of master or slaves
					print 'P2P ' + data
			else:
				break

if __name__ == '__main__':
	FPS = 60

	HOST = '127.0.0.1'
	PORT = 1789
	LISTEN_PORT = 1790
	
	import time
	c = NetClient(HOST, PORT, LISTEN_PORT)
	username = raw_input("USERNAME:\n")
	password = raw_input("PASSWORD:\n")
	c.auth(username, password)
	while True:
		c.step()
		time.sleep(1.0/FPS)
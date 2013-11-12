#!/usr/bin/python
# -*- coding: utf-8 -*-
# Central server script used to:
# - authorize bas on a REDIS base of users
# - centralize all games and save them to REDIS
# - UDP hole punch (get public ip address + user port)

from net.UDP import UDP
import redis



DB = redis.StrictRedis(host='localhost', port=6379, db=0)
GRYMARK_KEY = "grymark:"

GAMELIST = []
GAMELIST_MASTERS = {}
SERVER_MESSAGE = "tty, at your service"

class AuthPunchUDP(UDP):
	def __init__(self, host, port, binding_port):
		super(AuthPunchUDP, self).__init__(host, port, binding_port)

		self.addr_to_username = {}
		self.username_to_addr = {}

	def add(self, username, addr):
		self.addr_to_username[addr] =  username
		self.username_to_addr[username] = addr
	
	def remove(self, username, addr):
		del self.addr_to_username[addr]
		del self.username_to_addr[username]

	def authorize(self, username, password, addr):
		p = DB.get(GRYMARK_KEY + username)
		if p != None and p == password:
			print 'AUTH '+ username
			self.add(username, addr)
			return True
		return False
	
	def isAuthorized(self, addr):
		return addr in self.addr_to_username

	def reqAuth(self, addr, username, password):	
		self.response(addr, 'auth', authorized=self.authorize(username, password, addr))

	def reqGameList(self, addr):
		print 'GAMELIST ' + self.addr_to_username[addr]
		self.response(addr, 'gameList', content=GAMELIST, serverMessage=SERVER_MESSAGE)

	def reqCreateGame(self, addr, name):
		# TODO sanitize name and check type
		# send confirmation/rejection
		if name in GAMELIST:
			pass
		else:
			GAMELIST.append(name)
			#self.reqGameList(addr) # REMOVE !!!!!!!!!!!!!!!!!!!!!!!
			GAMELIST_MASTERS[name] = self.addr_to_username[addr] 

	def reqJoinGame(self, addr, name):
		if name in GAMELIST:
			# connect to game master
			if self.addr_to_username[addr] != GAMELIST_MASTERS[name]:
				self.connectP2P(self.addr_to_username[addr], GAMELIST_MASTERS[name])
		else:
			pass #TODO

	def connectP2P(self, p1, p2):
		"""connect two players by name in peer-to-peer,
			p1 is slave and p2 master
			it's UDP so no actual connection, it's more like
			now we know how to contact each other
		"""
		print 'CONNECTING ' + p1 + ' and ' + p2
		addr1 = self.username_to_addr[p1]
		addr2 = self.username_to_addr[p2]
		print str(addr1)+str(addr2)

		self.response(addr1, 'connectToMaster', address=addr2, username=p2)
		self.response(addr2, 'connectToSlave', address=addr1, username=p1)


	def step(self):
		self.update()
		while True:
			msg = self.recv()
			if msg != None:
				data, addr = msg
				try:
					if self.isAuthorized(addr) or data['cmd'] == 'auth':
						if 'arg' in data:
							getattr(self, 'req' + data['cmd'][:1].upper() + data['cmd'][1:])(addr, **data['arg'])
						else:
							getattr(self, 'req' + data['cmd'][:1].upper() + data['cmd'][1:])(addr)
					else:
						print data['cmd'] + ' refused to ' + str(addr)
				except Exception, err:
					print err
			else:
				break




if __name__ == '__main__':
	HOST = '127.0.0.1'
	PORT = 1790
	LISTEN_PORT = 1789
	FPS=60
	import time
	c = AuthPunchUDP(HOST, PORT, LISTEN_PORT)
	
	while True:
		c.step()
		time.sleep(1.0/FPS)
#!/usr/bin/python
# -*- coding: utf-8 -*-

import msgpack
import socket
from select import select

class UDP(object):
	def __init__(self, distant_host='127.0.0.1', distant_port=1789, binding_port=1789):
		self.distant_host = distant_host
		self.distant_port = distant_port
		self.msg_queue = []
		self.addr_list = set([])

		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.bind(binding_port)
	def bind(self, binding_port):
		self.s.bind(("", binding_port))

	def sendServer(self, msg):
		self.s.sendto(msgpack.packb(msg), (self.distant_host, self.distant_port))

	def sendClients(self, msg):
		for addr in self.addr_list:
			self.s.sendto(msgpack.packb(msg), addr)

	def send(self, msg, addr):
		self.s.sendto(msgpack.packb(msg), addr)
	
	def recv(self):	
		if self.msg_queue == []:
			return None
		else:
			return self.msg_queue.pop(0)
	def update(self):
		while True: # receive everything there is to read
			rfds,_,_ = select([self.s], [], [], 0)
			if rfds != []:
				try:
					data, addr = self.s.recvfrom(4096)
					self.msg_queue.append((msgpack.unpackb(data), addr))
					self.addr_list.add(addr)
					#TODO congestion control, what happens with > 4096
					#TODO remove addr from list if "connection" closed 
				except:
					pass #TODO send ping and disconnect if no answer
			else:
				break

	def request(self, func, **arg):
		if arg:
			self.sendServer({'cmd':func, 'arg':arg})
		else:
			self.sendServer({'cmd':func})

	def response(self, addr, func, **arg):
		if arg:
			self.send({'cmd':func, 'arg':arg}, addr)
		else:
			self.send({'cmd':func}, addr)

	def close(self):
		self.s.close()
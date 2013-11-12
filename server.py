from server.server import AuthPunchUDP


HOST = '127.0.0.1'
PORT = 1790
LISTEN_PORT = 1789
FPS=60

if __name__ == '__main__':
	import time
	c = AuthPunchUDP(HOST, PORT, LISTEN_PORT)
	
	while True:
		c.step()
		time.sleep(1.0/FPS)
from constants import FPS

from math import floor


class Counter():

	FRAME_CNT = 0

	def __init__(self, countdown=0):
		# Time in milliseconds => convert in frames
		self.countdown = int((countdown/1000.0)*FPS)
		self.paused = False

		self.frameElapsed = 0	# Total frame elapsed since start
		self.framePaused = 0	# Total frame elapsed during pause
		self.refPause = 0		# Pause start


	def start(self):
		self.ref = Counter.FRAME_CNT

	def time(self):
		""" Returns elapsed number of frames since start """
		if not self.paused:
			self.frameElapsed = Counter.FRAME_CNT-self.ref-self.framePaused


	def pause(self):
		if not self.paused:
			self.refPaused = Counter.FRAME_CNT
			self.paused = True

	def unpause(self):
		if self.paused:
			self.framePaused += Counter.FRAME_CNT-self.refPaused 
			self.paused = False


	def timeOut(self):
		""" Returns true if time elapsed """
		self.time()
		return True if self.frameElapsed-self.countdown >= 0 else False

	def underTime(self, frameRef):
		""" Returns true if elapsed number of frames under parameter value """
		return True if frameRef-self.frameElapsed >= 0 else False

	def getFrameNb(self):
		""" Returns number of elapsed frames """
		self.time()
		return self.frameElapsed

	def getSeconds(self):
		""" Returns time elapsed in seconds """
		self.time()
		return self.frameElapsed/FPS

	def getMilliSeconds(self):
		""" Returns time elapsed in milliseconds """
		self.time()
		return self.frameElapsed*1000.0/FPS


	
	def formatCounter(self, nDec=3):
		""" Returns printable time elapsed with nDec decimals """
		self.time()
		time = self.frameElapsed*1000/FPS

		# Get each parts of the time
		mn = str((time/1000)/60)
		sec = str((time/1000)%60)
		ms = str(time%1000)

		# Format time: MM:SS:mmm
		mn = mn if len(mn) == 2 else '0'+mn
		sec = sec if len(sec) == 2 else '0'+sec
		ms = ms if len(ms) == 3 else ('0'+ms if len(ms) == 2 else '00'+ms)


		return mn + ':' + sec + ':' + ms[:nDec]

	@staticmethod
	def staticFormat(t, nDec=3):
		""" Returns printable time from number of frames """
		time = t*1000/FPS

		# Get each parts of the time
		mn = str((time/1000)/60)
		sec = str((time/1000)%60)
		ms = str(time%1000)

		# Format time: MM:SS:mmm
		mn = mn if len(mn) == 2 else '0'+mn
		sec = sec if len(sec) == 2 else '0'+sec
		ms = ms if len(ms) == 3 else ('0'+ms if len(ms) == 2 else '00'+ms)


		return mn + ':' + sec + ':' + ms[:nDec]


	@staticmethod
	def formatTime(time):
		""" Returns printable time in milliseconds format MM:SS:mmm """

		frmTime = ''
		
		# Get floor
		time = int(time)
		# Get each parts of the time
		mn = str((time/1000)/60)
		sec = str((time/1000)%60)
		ms = str(time%1000)

		# Format time: MM:SS:mmm
		# Minutes
		for i in range(2-len(mn)):
			frmTime += '0'
		frmTime += mn
		# Seconds
		frmTime += ':'
		for i in range(2-len(sec)):
			frmTime += '0'
		frmTime += sec
		# Milliseconds
		frmTime += ':'
		for i in range(3-len(ms)):
			frmTime += '0'
		frmTime += ms

		return frmTime


	@staticmethod
	def getFrameFromSec(seconds):
		""" Converts seconds to number of frames """
		return seconds*FPS
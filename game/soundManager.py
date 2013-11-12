import pygame

#NOTE: mp3 is not fully supported, convert to .ogg instead

class SoundManager:
	"""Play music (streaming, only one) or sound effects"""

	def __init__(self, soundFolder=""):
		pygame.mixer.init(44100, -16, 1, 512)

		self._sounds = {}
		self._soundFolder = soundFolder


	def playMusic(self, music):
		pygame.mixer.music.load(self._soundFolder+music)
		pygame.mixer.music.play()

	def stopMusic(self):
		pygame.mixer.music.stop()

	def load(self, sound):
		self._sounds[sound] = pygame.mixer.Sound(self._soundFolder+sound)

	def play(self, sound):
		if sound in self._sounds:
			try:
				self._sounds[sound].play()
			except:
				print 'sound not found: '+sound

	def stop(self, sound):
		if sound in self._sounds:
			self._sounds[sound].stop()

	def loadAllSounds(self):
		self.load("ballPad.ogg")
		self.load("brickHit.ogg")
		self.load("indestructibleHit.ogg")
		self.load("lifeLost.ogg")
		self.load("metalBounce.ogg")
		self.load("objectHit.ogg")
		self.load("ballWall.wav")
		self.load("score.ogg")
		self.load("score2.ogg")
		self.load("scoreCounting.ogg")
		self.load("toughBrickHit.ogg")
		self.load("powerup.ogg")
		self.load("blip1.ogg")
		self.load("blip2.ogg")
		self.load("button1.ogg")
		self.load("button2.ogg")
		self.load("button3.ogg")
		self.load("button4.ogg")
		self.load("scoreCounting.wav")
		self.load("new_record.ogg")
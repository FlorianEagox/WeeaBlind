from enum import Enum, auto
# from TTS.api import TTS
import pyttsx3

from espeakng import ESpeakNG

class Voice:
	class VoiceType(Enum):
		ESPEAK = auto()
		COQUI = auto()
		SAPI5 = auto()
	speed = 0
	voice = None
	def __init__(self, voice_type, init_args=[], name="Unnamed"):
		self.voice_type = voice_type
		self.name = name
		if voice_type == self.VoiceType.ESPEAK:
			self.voice = ESpeakNG()
			self.set_voice_params(init_args)
		elif voice_type == self.VoiceType.COQUI:
			self.voice = TTS(init_args)
		elif voice_type == self.VoiceType.SAPI5:
			self.voice = pyttsx3.init(*init_args)
			print(self.voice.getProperty('voices'))
	def speak(self, text, file_name):
		if self.voice_type == self.VoiceType.ESPEAK:
			self.voice.synth_wav(text, file_name)
		elif self.voice_type == self.VoiceType.COQUI:
			self.voice.tts_to_file(text, file_path=file_name)
		elif self.voice_type == self.VoiceType.SAPI5:
			self.voice.save_to_file(text, file_name)
			self.voice.runAndWait()
	def set_speed(self, speed):
		self.speed, self.voice.speed = speed
	
	def set_voice_params(self, voice=None, pitch=None):
		if(self.voice_type == self.VoiceType.ESPEAK):
			if voice: self.voice.voice = voice
			if pitch: self.voice.pitch = pitch
		if(self.voice_type == self.VoiceType.SAPI5):
			self.voice.setProperty('voice', self.voice.getProperty('voices')[voice].id)
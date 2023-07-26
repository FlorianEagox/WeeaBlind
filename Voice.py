from enum import Enum, auto
from espeakng import ESpeakNG


class Voice:
	class VoiceType(Enum):
		ESPEAK = auto()
		COQUI = auto()
	speed = 0
	voice = None
	def __init__(self, voice_type, init_args):
		self.voice_type = voice_type
		if voice_type == self.VoiceType.ESPEAK:
			self.voice = ESpeakNG()
			self.set_voice_params(init_args)
		elif voice_type == self.VoiceType.COQUI:
			tts = TTS(init_args)
	def speak(self, text, file_name):
		if self.voice_type == self.VoiceType.ESPEAK:
			self.voice.synth_wav(text, file_name)
		elif self.voice_type == self.VoiceType.COQUI:
			self.voice.tts_to_file(text, file_path=file_name)
	
	def set_speed(self, speed):
		self.speed, self.voice.speed = speed
	
	def set_voice_params(self, voice=None, pitch=None):
		if(self.voice_type == self.VoiceType.ESPEAK):
			if voice: self.voice.voice = voice
			if pitch: self.voice.pitch = pitch

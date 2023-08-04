from enum import Enum, auto
import abc
from TTS.api import TTS
import pyttsx3
from espeakng import ESpeakNG

class Voice(abc.ABC):
    class VoiceType(Enum):
        ESPEAK = "ESpeak"
        COQUI = "Coqui TTS"
        SAPI5 = "Microsoft SAPI5"

    def __new__(cls, voice_type, init_args=[], name="Unnamed"):
        if cls is Voice:
            if voice_type == cls.VoiceType.ESPEAK:
                return super().__new__(ESpeakVoice)
            elif voice_type == cls.VoiceType.COQUI:
                return super().__new__(CoquiVoice)
            elif voice_type == cls.VoiceType.SAPI5:
                return super().__new__(SAPI5Voice)
        else:
            return super().__new__(cls)

    def __init__(self, voice_type, init_args=[], name="Unnamed"):
        self.voice_type = voice_type
        self.name = name

    @abc.abstractmethod
    def speak(self, text, file_name):
        pass

    @abc.abstractmethod
    def set_speed(self, speed):
        pass

    @abc.abstractmethod
    def set_voice_params(self, voice=None, pitch=None):
        pass

    @abc.abstractmethod
    def list_voice_options(self):
        pass

class ESpeakVoice(Voice):
    def __init__(self, init_args=[], name="Unnamed"):
        super().__init__(Voice.VoiceType.ESPEAK, init_args, name)
        self.set_voice_params(init_args)

    def speak(self, text, file_name):
        self.voice.synth_wav(text, file_name)

    def set_speed(self, speed):
        self.voice.speed = speed

    def set_voice_params(self, voice=None, pitch=None):
        if voice:
            self.voice.voice = voice
        if pitch:
            self.voice.pitch = pitch

    def list_voice_options(self):
        # Optionally, you can return available voice options for ESpeak here
        pass

class CoquiVoice(Voice):
    def __init__(self, init_args=[], name="Unnamed"):
        super().__init__(Voice.VoiceType.COQUI, init_args, name)
        self.voice = TTS()

    def speak(self, text, file_name):
        self.voice.tts_to_file(text, file_path=file_name)

    def set_speed(self, speed):
        self.speed = speed

    def set_voice_params(self, voice=None):
        self.voice.load_tts_model_by_name(voice)

    def list_voice_options(self):
        return TTS.list_models()

class SAPI5Voice(Voice):
    def __init__(self, init_args=[], name="Unnamed"):
        super().__init__(Voice.VoiceType.SAPI5, init_args, name)
        self.voice = pyttsx3.init(*init_args)

    def speak(self, text, file_name):
        self.voice.save_to_file(text, file_name)
        self.voice.runAndWait()

    def set_speed(self, speed):
        self.voice.setProperty('rate', speed)

    def set_voice_params(self, voice=None, pitch=None):
        if voice:
            self.voice.setProperty('voice', self.voice.getProperty('voices')[voice].id)

    def list_voice_options(self):
        return [voice.name for voice in self.voice.getProperty('voices')]

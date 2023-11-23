# This file is just a quick script for whatever I'm testing at the time, it's not really important 

# testing XTTS / VC models

from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to('cuda')

# generate speech by cloning a voice using default settings
tts.tts_to_file(text="Welcome to DougDoug, where we solve problems that no one has",
                file_path="/media/tessa/SATA SSD1/AI MODELS/cloning/output/doug.wav",
                speaker_wav="/media/tessa/SATA SSD1/AI MODELS/cloning/doug.wav",
                language="en")
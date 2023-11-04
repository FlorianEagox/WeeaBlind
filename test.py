# This file is just a quick script for whatever I'm testing at the time, it's not really important 

# testing XTTS / VC models

from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v1.1").to('cuda')

# generate speech by cloning a voice using default settings
tts.tts_to_file(text="boymoder femboys who take estrogen are more trans than passoids who don’t take any kind of HRT and are more true trans than non-binary hons who go by binary pronouns as well as pre-transition egg femboys",
                file_path="/media/tessa/SATA SSD1/AI MODELS/cloning/output/squid3.wav",
                speaker_wav="/media/tessa/SATA SSD1/AI MODELS/cloning/squid2.wav",
                language="en")
import srt
from TTS.api import TTS
import numpy as np
from espeakng import ESpeakNG
import re

from pydub import AudioSegment

start_time = 94
end_time =  124 #1324
CLEANR = re.compile('<.*?>')

# READ SUBS
raw_subs = ""
with open("out.srt","r") as f:
	raw_subs = srt.parse(f.read())
subs = list(raw_subs)

# READ DIARY FILE
speech_diary = []
with open('audio.rttm', 'r') as diary_file:
	for line in diary_file.read().strip().split('\n'):
		line_values = line.split(' ')
		speech_diary.append([line_values[7], float(line_values[3]), float(line_values[4])])
# print(speech_diary)


def find_nearest(array, value):
	array = np.asarray(array)
	return (np.abs(array - value)).argmin()

start_line = find_nearest([sub.start.total_seconds() for sub in subs], start_time)
end_line = find_nearest([sub.start.total_seconds() for sub in subs], end_time)
speech_diary_adjusted = [[line[0], line[1] + subs[start_line].start.total_seconds(), line[2]] for line in speech_diary]

# Create unique speakers
total_speakers = len(set(line[0] for line in speech_diary))
speakers = []
for i in range(total_speakers):
	speakers.append(ESpeakNG(voice='en'))

speakers[1].voice = 'en-us'
speakers[2].pitch = 90

total_duration = (end_time - start_time)*1000
# empty_audio = AudioSegment.silent(duration=total_duration)
empty_audio = AudioSegment.from_file('saiki.mkv')

tts = TTS(model_path='/home/tessa/Downloads/LibriTTS', config_path='/home/tessa/Downloads/LibriTTS/config.json') #TTS.list_models()[8]) # 8 13

# Synth
def synth():
	for sub in subs[start_line:end_line]:
		text = re.sub(CLEANR, '', sub.content)
		current_speaker = int(speech_diary_adjusted[find_nearest([line[1] for line in speech_diary_adjusted], sub.start.total_seconds())][0].split('_')[1])
		speed = 60*int((len(text.split(' ')) / (sub.end.total_seconds() - sub.start.total_seconds())))
		speakers[current_speaker].speed = speed
		file_name = f"files/{sub.index}.wav"
		# speakers[current_speaker].synth_wav(text, file_name)
		print(text)
		tts.tts_to_file(text, file_path=file_name)
		# empty_audio = empty_audio.overlay(AudioSegment.from_file(file_name), position=sub.start.total_seconds()*1000)
	# empty_audio.export("out.wav")

# synth()
# print('\n\nSPEAKERS\n', tts.speakers)

# GET THE SUBS
# stream = ffmpeg.input("./saiki.mkv")

# INITIALIZE THE MODELS

# for (index, model) in enumerate(TTS.list_models()):
# 	TTS.voc
# 	if '/en/' in model:
# 		print(index, model)

tts.tts_to_file("This do be a new test!", 'owo.wav')

# def tts_thread(text, filename):
# 	tts.tts_to_file(text, file_path=filename)
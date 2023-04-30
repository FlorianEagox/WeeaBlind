import srt
from TTS.api import TTS
import numpy as np
from espeakng import ESpeakNG
import re

start_time = 94
end_time = 114
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

# Synth
for sub in subs[start_line:end_line]:
	text = re.sub(CLEANR, '', sub.content)
	current_speaker = int(speech_diary_adjusted[find_nearest([line[1] for line in speech_diary_adjusted], sub.start.total_seconds())][0].split('_')[1])
	speed = int((len(text) / (sub.end.total_seconds() - sub.start.total_seconds())))
	# speakers[current_speaker].wpm = speed
	speakers[current_speaker].synth_wav(text, f"./files/{sub.index}.wav")

def speak(speaker, rate, output):
	return


# GET THE SUBS
# stream = ffmpeg.input("./saiki.mkv")

# INITIALIZE THE MODELS
# tts = TTS(TTS.list_models()[10])
# # for index, model in enumerate(TTS.list_models()):
# # 	print(index, model)
# tts.tts_to_file("This do be a test!", file_path="owo.wav")

# def tts_thread(text, filename):
# 	tts.tts_to_file(text, file_path=filename)
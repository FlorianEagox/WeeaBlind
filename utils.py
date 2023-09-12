import os.path
import numpy as np
from pydub.playback import play
from pydub import AudioSegment
from torch.cuda import is_available

APP_NAME = "WeeaBlind"
test_video_name = "./output/download.webm"
default_sample_path = "./output/sample.wav"
test_start_time = 94
test_end_time =  1324
gpu_detected = is_available()

def create_output_dir():
	path = './output/files'
	if not os.path.exists(path):
		os.makedirs(path)

def get_output_path(input, suffix, prefix='', path=''):
	filename = os.path.basename(input)
	filename_without_extension = os.path.splitext(filename)[0]
	return os.path.join('output', path, f"{prefix}{filename_without_extension}{suffix}")

def timecode_to_seconds(timecode):
	parts = list(map(float, timecode.split(':')))
	seconds = parts[-1]
	if len(parts) > 1:
		seconds += parts[-2] * 60
	if len(parts) > 2:
		seconds += parts[-3] * 3600
	return seconds

def seconds_to_timecode(seconds):
	hours = int(seconds // 3600)
	minutes = int((seconds % 3600) // 60)
	seconds = seconds % 60
	timecode = ""
	if hours:
		timecode += f"{hours}:"
	if minutes:
		timecode += f"{minutes}:" 
	timecode = f"{timecode}{seconds:05.2f}"
	return timecode

# Finds the closest element in an arry to the given value
def find_nearest(array, value):
	return (np.abs(np.asarray(array) - value)).argmin()

def sampleVoice(text, speaker, output=default_sample_path):
	play(AudioSegment.from_file(speaker.speak(text, output)))


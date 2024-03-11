import os.path
import app_state
import numpy as np
from pydub.playback import play
from pydub import AudioSegment
import feature_support
import sys

APP_NAME = "WeeaBlind"
test_video_name = "./output/download.webm"

test_start_time = 94
test_end_time =  1324
gpu_detected = feature_support.gpu_supported

root = __file__
if getattr(sys, 'frozen', False):
	application_path = os.path.dirname(sys.executable)
	print("NEW PATH", application_path)
	os.chdir(application_path)
	root = sys.executable

def create_output_dir():
	path = './output/files'
	if not os.path.exists(path):
		os.makedirs(path)

def get_output_path(input, suffix, prefix='', path=''):
	filename = os.path.basename(input)
	filename_without_extension = os.path.splitext(filename)[0]
	return os.path.join(os.path.dirname(os.path.abspath(root)), 'output', path, f"{prefix}{filename_without_extension}{suffix}")

default_sample_path = get_output_path("sample", ".wav")
print(default_sample_path)

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

def sampleVoice(text, output=default_sample_path):
	play(AudioSegment.from_file(app_state.sample_speaker.speak(text, output)))

snippet_export_path = get_output_path("video_snippet", ".wav")
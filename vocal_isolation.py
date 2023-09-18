from spleeter.separator import Separator
from spleeter.audio import adapter
from pydub import AudioSegment
import numpy as np
import utils

separator = Separator('spleeter:2stems')
def seperate_ram(video):
	audio_loader = adapter.AudioAdapter.default()
	sample_rate = 44100
	audio = video.audio
	# arr = np.array(audio.get_array_of_samples(), dtype=np.float32).reshape((-1, audio.channels)) / (
	#         1 << (8 * audio.sample_width - 1)), audio.frame_rate
	arr = np.array(audio.get_array_of_samples())
	audio, _ = audio_loader.load_waveform(arr)
	# waveform, _ = audio_loader.load('/path/to/audio/file', sample_rate=sample_rate)

	print("base audio\n", base_audio, "\n")
	# Perform the separation :
	# prediction = separator.separate(audio)

def seperate_file(video):
	source_audio_path = utils.get_output_path(video.file, '-audio.wav')
	separator.separate_to_file(
		video.audio.export(source_audio_path, format="wav").name,
		'./output/',
		filename_format='{filename}-{instrument}.{codec}'
	)
	video.background_track = utils.get_output_path(source_audio_path, '-accompaniment.wav')
	video.vocal_track = utils.get_output_path(source_audio_path, '-vocals.wav')

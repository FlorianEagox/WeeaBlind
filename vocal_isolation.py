import feature_support

if feature_support.vocal_isolation_supported:
	from spleeter.separator import Separator
	from spleeter.audio import adapter
from pydub import AudioSegment
import numpy as np
import utils

separator = None # Separator('spleeter:2stems')
# I don't have any clue on how to make this work yet, just ignore for now. Ideally we'd never have to serialize the audio to wav and then rea read it but alas, bad implementations of PCM will be the death of me
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

def seperate_file(video, isolate_subs=True):
	global separator
	if not separator:
		separator = Separator('spleeter:2stems')
	source_audio_path = utils.get_output_path(video.file, '-audio.wav')
	isolated_path = utils.get_output_path(video.file, '-isolate.wav')
	separator.separate_to_file(
		(video.audio).export(source_audio_path, format="wav").name,
		utils.get_output_path('.'),
		filename_format='{instrument}.{codec}'
	)
	# separator.separate_to_file(
	# 	video.isolate_subs().export(source_audio_path, format="wav").name,
	# 	'./output/',
	# 	filename_format='{filename}-{instrument}.{codec}'
	# )
	background_track = utils.get_output_path('accompaniment', '.wav')
	# If we removed primary langauge subs from a multilingual video, we'll need to add them back to the background.
	if video.subs_removed:
		background = AudioSegment.from_file(background_track)
		for sub in video.subs_removed:
			background = background.overlay(video.get_snippet(sub.start, sub.end), int(sub.start*1000))
		background.export(background_track, format="wav")
	video.background_track = background_track
	video.vocal_track = utils.get_output_path('vocals', '.wav')

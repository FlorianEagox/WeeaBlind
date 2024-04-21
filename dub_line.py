from dataclasses import dataclass
import ffmpeg
import utils
import app_state
import srt
from re import compile, sub as substitute
from pydub import AudioSegment
from audiotsm import wsola
from audiotsm.io.wav import WavReader, WavWriter
from audiotsm.io.array import ArrayReader, ArrayWriter
import numpy as np
from language_detection import detect_language

remove_xml = compile(r'<[^>]+>|\{[^}]+\}')
language_identifier_model = None # EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")

@dataclass
class DubbedLine:
	start: float
	end: float
	text: str
	index: int
	voice: int = 0
	language: str = ""

	def update_voice(self, voice):
		self.voice = voice

	# This is highly inefficient as it writes and reads the same file many times
	def dub_line_file(self, match_rate=True, match_volume=True, output=False):
		output_path = utils.get_output_path(str(self.index), '.wav', path='files')
		tts_audio = app_state.speakers[self.voice].speak(self.text, output_path)
		if match_rate and not self.end == -1:
			rate_adjusted = self.match_rate(tts_audio, self.end-self.start)
			segment = AudioSegment.from_wav(rate_adjusted)
		else:
			segment = AudioSegment.from_wav(tts_audio)
		if match_volume:
			segment = self.match_volume(app_state.video.get_snippet(self.start, self.end), segment)
		if output:
			segment.export(output_path, format='wav')
		return segment, output_path

	# This should ideally be a much more efficient way to dub.
	# All functions should pass around numpy arrays rather than reading and writting files. For some reason though, it gives distroted results
	def dub_line_ram(self, output=True):
		output_path = utils.get_output_path(str(self.index), '.wav', path='files')
		tts_audio = app_state.speakers[self.voice].speak(self.text)
		rate_adjusted = self.match_rate_ram(tts_audio, self.end-self.start)
		data = rate_adjusted / np.max(np.abs(rate_adjusted))
		# This causes some kind of wacky audio distrotion we NEED to fix ;C
		audio_as_int = (data * (2**15)).astype(np.int16).tobytes()
		segment = AudioSegment(
			audio_as_int,
			frame_rate=22050,
			sample_width=2,
			channels=1
		)
		if output:
			segment.export(output_path, format='wav')
		return segment

	def match_rate(self, target_path, source_duration, destination_path=None, clamp_min=0, clamp_max=4):
		if destination_path == None:
			destination_path = target_path.split('.')[0] + '-timeshift.wav'
		duration = float(ffmpeg.probe(target_path)["format"]["duration"])
		rate = duration*1/source_duration
		rate = np.clip(rate, clamp_min, clamp_max)
		with WavReader(target_path) as reader:
			with WavWriter(destination_path, reader.channels, reader.samplerate) as writer:
				tsm = wsola(reader.channels, speed=rate)
				tsm.run(reader, writer)
		return destination_path

	def match_rate_ram(self, target, source_duration, outpath=None, clamp_min=0.8, clamp_max=2.5):
		num_samples = len(target)
		target = target.reshape(1, num_samples)
		duration = num_samples / 22050
		rate = duration*1/source_duration
		rate = np.clip(rate, clamp_min, clamp_max)
		reader = ArrayReader(target)
		tsm = wsola(reader.channels, speed=rate)
		if not outpath:
			rate_adjusted = ArrayWriter(channels=1)
			tsm.run(reader, rate_adjusted)
			return rate_adjusted.data
		else:
			rate_adjusted = WavWriter(outpath, 1, 22050)
			tsm.run(reader, rate_adjusted)
			rate_adjusted.close()
			return outpath

	def match_volume(self, source_snippet, target):
		# ratio = source_snippet.rms / (target.rms | 1)
		ratio = source_snippet.dBFS - target.dBFS
		# adjusted_audio = target.apply_gain(ratio)
		adjusted_audio = target + ratio
		return adjusted_audio
		# adjusted_audio.export(output_path, format="wav")

	def get_language(self, source_snippet):
		if not self.language:
			self.language = detect_language(source_snippet)
		return self.language


def filter_junk(subs, minimum_duration=0.1, remove_repeats=True):
	filtered = []
	previous = ""
	for sub in subs:
		if (sub.end - sub.start) > minimum_duration:
			if sub.text != previous:
				if previous and sub.text.split("\n")[0] in previous:
					sub.text = "".join(sub.text.split("\n")[-1:])
				filtered.append(sub)
		previous = sub.text
	return filtered

# This function is designed to handle two cases
#	1 We just have a path to an srt that we want to import
#	2 You have a file containing subs, but not srt (a video file, a vtt, whatever)
# 		In this case, we must extract or convert the subs to srt, and then read it in (export then import)
def load_subs(import_path="", extract_subs_path=False, filter=True):
	if extract_subs_path: # For importing an external subtitles file
		(
			ffmpeg
			.input(extract_subs_path)
			.output(import_path)
			.global_args('-loglevel', 'error')
			.run(overwrite_output=True)
		)
	with open(import_path, "r", encoding="utf-8") as f:
		original_subs = list(srt.parse(f.read()))
		return filter_junk([
			DubbedLine(
				sub.start.total_seconds(),
				sub.end.total_seconds(),
				substitute(remove_xml, '', sub.content),
				sub.index
			)
			for sub in original_subs
		])

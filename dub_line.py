from dataclasses import dataclass
from Voice import Voice
import ffmpeg
import utils
import app_state
import srt
from re import compile, sub as substitute
from pydub import AudioSegment
from audiotsm import wsola
from audiotsm.io.wav import WavReader, WavWriter
from audiotsm.io.array import ArrayReader, ArrayWriter
from speechbrain.pretrained import EncoderClassifier
import numpy as np

remove_xml = compile(r'<[^>]+>|\{[^}]+\}')
language_identifier_model = EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")

@dataclass
class DubbedLine:
	start: float
	end: float
	text: str
	index: int
	voice: int = 0

	def dub_line_ram(self, output=True):
		output_path = utils.get_output_path(str(self.index), '.wav', path='files')
		tts_audio = app_state.speakers[self.voice].speak(self.text)
		rate_adjusted = self.match_rate_ram(tts_audio, self.end-self.start)
		data = rate_adjusted / np.max(np.abs(rate_adjusted))
		audio_as_int = (data * (2**15)).astype(np.int16).tobytes()
		segment = AudioSegment(
			audio_as_int,
			frame_rate=22050,
			sample_width=2,
			channels=1
		)
		# segment = AudioSegment.from_wav(output_path)
		result = segment #match_volume(get_snippet(sub.start, sub.end), segment)
		if output:
			result.export(output_path, format='wav')
		return result

	def match_rate(self, target, source_duration, destination_path=None, clamp_min=0, clamp_max=4):
		if destination_path == None:
			destination_path = target.split('.')[0] + '-timeshift.wav'
		duration = float(ffmpeg.probe(target)["format"]["duration"])
		rate = duration*1/source_duration
		rate = np.clip(rate, clamp_min, clamp_max)
		with WavReader(target) as reader:
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

	def match_volume(source_snippet, target):
		ratio = source_snippet.rms / (target.rms | 1)
		# ratio = source_snippet.dBFS - target.dBFS
		adjusted_audio = target.apply_gain(ratio)
		# adjusted_audio = target + raio
		return adjusted_audio
		# adjusted_audio.export(output_path, format="wav")


def isnt_target_language(file, exclusion="English"):
	signal = language_identifier_model.load_audio(file)
	prediction = language_identifier_model.classify_batch(signal)
	return prediction[3][0].split(' ')[1] != exclusion

# This function is designed to handle two cases
#	1 We just have a path to an srt that we want to import
#	2 You have a file containing subs, but not srt (a video file, a vtt, whatever)
# 		In this case, we must extract or convert the subs to srt, and then read it in (export then import)
def load_subs(import_path="", extract_subs_path=False):
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
		return [
			DubbedLine(
				sub.start.total_seconds(),
				sub.end.total_seconds(),
				substitute(remove_xml, '', sub.content),
				sub.index
			)
			for sub in original_subs
		]

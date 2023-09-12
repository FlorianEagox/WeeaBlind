from dataclasses import dataclass
from Voice import Voice
import ffmpeg
# from synth import get_output_path, current_file
import srt
from re import compile, sub as substitute
from audiotsm import wsola
from audiotsm.io.wav import WavReader, WavWriter
from audiotsm.io.array import ArrayReader, ArrayWriter
from speechbrain.pretrained import EncoderClassifier
import numpy as np

remove_xml = compile(r'<[^>]+>|\{[^}]+\}')

@dataclass
class DubbedLine:
	start: float
	end: float
	text: str
	index: int
	voice: Voice = 0

	def post_process(self, file, source_start, source_end, adjust_volume=True):
		adjustment = match_rate(file, source_end-source_start)
		if adjust_volume:
			adjustment = match_volume(get_snippet(source_start, source_end), adjustment, adjustment)
		return adjustment

	def match_rate(target, source_duration, destination_path=None, clamp_min=0, clamp_max=4):
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

	def match_rate_ram(target, source_duration, outpath=None, clamp_min=0.8, clamp_max=2.5):
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

language_id = EncoderClassifier.from_hparams(source="speechbrain/lang-id-voxlingua107-ecapa", savedir="tmp")
def isnt_target_language(target="./output/video_snippet.wav", exclusion="English"):
	signal = language_id.load_audio(target)
	prediction = language_id.classify_batch(signal)
	return prediction[3][0].split(' ')[1] != exclusion

def load_subs(import_path=False, export=""):
	# export = get_output_path(current_file, '.srt')
	if import_path: # For importing an external subtitles file
		(
			ffmpeg
			.input(import_path)
			.output(export)
			.global_args('-loglevel', 'error')
			.run(overwrite_output=True)
		)
	with open(export, "r", encoding="utf-8") as f:
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

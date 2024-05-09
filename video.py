"""
The Video class represents a reference to a video from either a file or web link. This class should implement the ncessary info to dub a video.
"""
import time
import ffmpeg
from yt_dlp import YoutubeDL
import utils
from pydub import AudioSegment
from dub_line import load_subs
import random
from dub_line import DubbedLine

class Video:
	def __init__(self, video_URL, loading_progress_hook=print, lang=None):
		self.start_time = self.end_time = 0
		self.downloaded = False
		self.subs = self.subs_adjusted = self.subs_removed = []
		self.background_track = self.vocal_track = None
		self.speech_diary = self.speech_diary_adjusted = None
		self.load_video(video_URL, loading_progress_hook, lang)
		self.mixing_ratio = 1


	# This is responsible for loading the app's audio and subtitles from a video file or YT link
	def load_video(self, video_path, progress_hook=print, lang=None):
		sub_path = ""
		if video_path.startswith("http"):
			self.downloaded = True
			try:
				video_path, sub_path, self.yt_sub_streams = self.download_video(video_path, progress_hook, lang=lang)
			except: return
			progress_hook({"status":"complete"})
		else:
			self.downloaded = False
		self.file = video_path
		if not (self.downloaded and not sub_path):
			try:
				self.subs = self.subs_adjusted = load_subs(utils.get_output_path(self.file, '.srt'), sub_path or video_path)
			except:
				progress_hook({"status": "subless"})
		self.audio = AudioSegment.from_file(video_path)
		self.duration = float(ffmpeg.probe(video_path)["format"]["duration"])
		if self.subs:
			self.update_time(0, self.duration)

	def download_video(self, link, progress_hook=print, lang=None):
		options = {
			'outtmpl': 'output/%(id)s.%(ext)s',
			'writesubtitles': True,
			'writeautomaticsub': True,
			"progress_hooks": (progress_hook,),
			"listsubs": True
		}
		if lang:
			# options["writeautomaticsub"] = False
			options["subtitleslangs"] = (".*" + lang + ".*").split(',')
		else:
			options["subtitleslangs"] = ["all"]
		try:
			with YoutubeDL(options) as ydl:
				
				info = ydl.extract_info(link)
				output = ydl.prepare_filename(info)
				subs = info["subtitles"] | info["automatic_captions"]
				print("SUBS:", subs)
				subs = {k:v for k, v in subs.items() if v[-1].get("filepath", None)}
				print("Detected Subtitles\n", subs)
				return output, list(subs.values())[0][-1]["filepath"] if subs else None, subs
		except Exception as e:
			progress_hook({"status": "error", "error": e})
			raise e


	def update_time(self, start, end):
		self.start_time = start
		self.end_time = end
		# clamp the subs to the crop time specified
		start_line = utils.find_nearest([sub.start for sub in self.subs], start)
		end_line = utils.find_nearest([sub.start for sub in self.subs], end)
		self.subs_adjusted = self.subs[start_line:end_line]
		if self.speech_diary:
			self.update_diary_timing()

	def list_streams(self):
		probe = ffmpeg.probe(self.file)["streams"]
		if self.downloaded:
			subs = [{"name": stream[-1]['name'], "stream": stream[-1]['filepath']} for stream in self.yt_sub_streams.values()]
		else:
			subs = [{"name": stream['tags'].get('language', 'unknown'), "stream": stream['index']} for stream in probe if stream["codec_type"] == "subtitle"]
		return {
			"audio": [stream for stream in probe if stream["codec_type"] == "audio"],
			"subs": subs
		}

	def get_snippet(self, start, end):
		return self.audio[start*1000:end*1000]
	
	# Crops the video's audio segment to reduce memory size
	def crop_audio(self, isolated_vocals):
		# ffmpeg -i .\saiki.mkv -vn -ss 84 -to 1325 crop.wav
		source_file = self.vocal_track if isolated_vocals and self.vocal_track else self.file
		output = utils.get_output_path(source_file, "-crop.wav")
		(
			ffmpeg
			.input(self.file, ss=self.start_time, to=self.end_time)
			.output(output)
			.global_args('-loglevel', 'error')
			.global_args('-vn')
			.run(overwrite_output=True)
		)
		return output

	def detect_subs_lang(self, progress_hook=print):
		snippet_path = snippet_path = "video_snippet.wav" # utils.get_output_path('video_snippet', '.wav')
		for i, sub in enumerate(self.subs_adjusted):
			self.get_snippet(sub.start, sub.end).export(snippet_path, format="wav")
			sub.get_language(snippet_path)
			progress_hook(i, f"{i}/{len(self.subs_adjusted)}: {sub.text}")
		progress_hook(-1, "done")

	def filter_multilingual_subtiles(self, exclusion=["English"]):
		multi_lingual_subs = []
		removed_subs = []
		for i, sub in enumerate(self.subs_adjusted):
			if sub.language not in exclusion:
				multi_lingual_subs.append(sub)
			else:
				removed_subs.append(sub)
		self.subs_adjusted = multi_lingual_subs
		self.subs_removed = removed_subs

	# This funxion is is used to only get the snippets of the audio that appear in subs_adjusted after language filtration or cropping, irregardless of the vocal splitting.
	# This should be called AFTER filter multilingual and BEFORE vocal isolation. Not useful yet
	# OKAY THERE HAS TO BE A FASTER WAY TO DO THIS X_X

	# def isolate_subs(self):
	# 	base = AudioSegment.silent(duration=self.duration*1000, frame_rate=self.audio.frame_rate, channels=self.audio.channels, frame_width=self.audio.frame_width)
	# 	samples = np.array(base.get_array_of_samples())
	# 	frame_rate = base.frame_rate
		
	# 	for sub in self.subs_adjusted:
	# 		copy = np.array(self.get_snippet(sub.start, sub.end).get_array_of_samples())
	# 		start_sample = int(sub.start * frame_rate)
	# 		end_sample = int(sub.end * frame_rate)
			
	# 		# Ensure that the copy array has the same length as the region to replace
	# 		copy = copy[:end_sample - start_sample]  # Trim if necessary
			
	# 		samples[start_sample:end_sample] = copy

	# 	return AudioSegment(
	# 		samples.tobytes(),
	# 		frame_rate=frame_rate,
	# 		sample_width=base.sample_width,  # Adjust sample_width as needed (2 bytes for int16)
	# 		channels=base.channels
	# 	)

	def isolate_subs(self, subs):
		empty_audio = AudioSegment.silent(self.duration * 1000, frame_rate=self.audio.frame_rate)
		empty_audio = self.audio
		first_sub = subs[0]
		empty_audio = empty_audio[0:first_sub.start].silent((first_sub.end-first_sub.start)*1000)
		for i, sub in enumerate(subs[:-1]):
			print(sub.text)
			empty_audio = empty_audio[sub.end:subs[i+1].start].silent((subs[i+1].start-sub.end)*1000, frame_rate=empty_audio.frame_rate, channels=empty_audio.channels, sample_width=empty_audio.sample_width, frame_width=empty_audio.frame_width)

		return empty_audio

	def run_dubbing(self, progress_hook=None, match_rate=True):
		total_errors = 0
		operation_start_time = time.process_time()
		empty_audio = AudioSegment.silent(self.duration * 1000, frame_rate=22050)
		status = ""
		# with concurrent.futures.ThreadPoolExecutor(max_workers=100) as pool:
		# 	tasks = [pool.submit(dub_task, sub, i) for i, sub in enumerate(subs_adjusted)]		
		# 	for future in concurrent.futures.as_completed(tasks):
		# 		pass
		for i, sub in enumerate(self.subs_adjusted):
			status = f"{i}/{len(self.subs_adjusted)}"
			progress_hook(i, f"{status}: {sub.text}")
			try:
				line = sub.dub_line_file(match_rate=match_rate, match_volume=False)[0]
				empty_audio = empty_audio.overlay(line, sub.start*1000)
			except Exception as e:
				print(e)
				total_errors += 1
		self.dub_track = empty_audio.export(utils.get_output_path(self.file, '-dubtrack.wav'), format="wav").name
		progress_hook(i+1, "Mixing New Audio")
		self.mix_av(mixing_ratio=self.mixing_ratio)
		progress_hook(-1)
		print(f"TOTAL TIME TAKEN: {time.process_time() - operation_start_time}")
		# print(total_errors)

	# This runs an ffmpeg command to combine the audio, video, and subtitles with a specific ratio of how loud to make the dubtrack
	def mix_av(self, mixing_ratio=1, dubtrack=None, output_path=None):
		# i hate python, plz let me use self in func def
		if not dubtrack: dubtrack = self.dub_track
		if not output_path: output_path = utils.get_output_path(self.file, '-dubbed.mkv')

		input_video = ffmpeg.input(self.file)
		input_audio = input_video.audio
		if self.background_track:
			input_audio = ffmpeg.input(self.background_track)
		input_dub = ffmpeg.input(dubtrack).audio

		mixed_audio = ffmpeg.filter([input_audio, input_dub], 'amix', duration='first', weights=f"1 {mixing_ratio}")

		output = (
			# input_video['s']
			ffmpeg.output(input_video['v'], mixed_audio, output_path, vcodec="copy", acodec="aac")
			.global_args('-loglevel', 'error')
			.global_args('-shortest')
		)
		ffmpeg.run(output, overwrite_output=True)

	# Change the subs to either a file or a different stream from the video file
	def change_subs(self, stream_index=-1, external_path=""):
		if external_path:
			convert_srt_path = utils.get_output_path(external_path, '.srt')
			ffmpeg.input(external_path).output(convert_srt_path).run(overwrite_output=True)
			self.subs = self.subs_adjusted = load_subs(convert_srt_path)
			return
		if self.downloaded:
			sub_path = list(self.yt_sub_streams.values())[stream_index][-1]['filepath']
			self.subs = self.subs_adjusted = load_subs(utils.get_output_path(sub_path, '.srt'), sub_path)
		else:
			# ffmpeg -i output.mkv -map 0:s:1 frick.srt
			sub_path = utils.get_output_path(self.file, '.srt')
			ffmpeg.input(self.file).output(sub_path, map=f"0:s:{stream_index}").run(overwrite_output=True)
			self.subs = self.subs_adjusted = load_subs(sub_path)

	def change_audio(self, stream_index=-1):
		audio_path = utils.get_output_path(self.file, f"-${stream_index}.wav")
		ffmpeg.input(self.file).output(audio_path, map=f"0:a:{stream_index}").run(overwrite_output=True)
		self.audio = AudioSegment.from_file(audio_path)

	def export_clone(self, snippets, path):
		empty_audio = AudioSegment.empty()
		for snippet in snippets:
			empty_audio += AudioSegment.silent()
			empty_audio += self.get_snippet(snippet.start, snippet.end)
		empty_audio.export(path, "wav")

	def sample_mixing(self) -> AudioSegment:
		random_test_sub: DubbedLine = random.choice(self.subs_adjusted)
		dubbed_audio, output_path = random_test_sub.dub_line_file()
		self.get_snippet(random_test_sub.start, random_test_sub.end).export(utils.snippet_export_path, format="wav")
		source = ffmpeg.input(utils.snippet_export_path)
		overlayed_tts = ffmpeg.input(output_path)
		mixed_audio = ffmpeg.filter([source, overlayed_tts], 'amix', duration='first', weights=f"1 {self.mixing_ratio}")
		mixed_sample_path = utils.get_output_path("mixed_sample", ".wav")
		output = (
			ffmpeg.output(mixed_audio, mixed_sample_path)
			.global_args('-loglevel', 'error')
			.global_args('-shortest')
		)
		ffmpeg.run(output, overwrite_output=True)
		return AudioSegment.from_file(mixed_sample_path)

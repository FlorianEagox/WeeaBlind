"""
The Video class represents a reference to a video from either a file or web link. This class should implement the ncessary info to dub a video.
"""

import time
import ffmpeg
from yt_dlp import YoutubeDL
import utils
from pydub import AudioSegment
from dub_line import load_subs, isnt_target_language
import json
class Video:
	def __init__(self, video_URL, loading_progress_hook=None):
		self.start_time = self.end_time = 0
		self.downloaded = False
		self.subs = self.subs_adjusted = []
		self.speech_diary = self.speech_diary_adjusted = None
		self.load_video(video_URL, loading_progress_hook)


	# This is responsible for loading the app's audio and subtitles from a video file or YT link
	def load_video(self, video_path, progress_hook=None):
		sub_path = ""
		if video_path.startswith("http"):
			self.downloaded = True
			try:
				video_path, sub_path, self.yt_sub_streams = self.download_video(video_path, progress_hook)
			except: return
			progress_hook({"status":"complete"})
		else:
			self.downloaded = False
		self.file = video_path
		if not (self.downloaded and not sub_path):
			self.subs = self.subs_adjusted = load_subs(utils.get_output_path(self.file, '.srt'), sub_path or video_path)
		self.audio = AudioSegment.from_file(video_path)
		self.duration = float(ffmpeg.probe(video_path)["format"]["duration"])
		if self.subs:
			self.update_time(0, self.duration)

	def download_video(self, link, progress_hook=print):
		options = {
			'outtmpl': 'output/%(id)s.%(ext)s',
			'writesubtitles': True,
			"subtitleslangs": ["all"],
			"progress_hooks": (progress_hook,)
		}
		try:
			with YoutubeDL(options) as ydl:
				info = ydl.extract_info(link)
				return ydl.prepare_filename(info), list(info["subtitles"].values())[0][-1]["filepath"] if info["subtitles"] else None, info["subtitles"]
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
	def crop_audio(self):
		# ffmpeg -i .\saiki.mkv -vn -ss 84 -to 1325 crop.wav
		output = utils.get_output_path(self.file, "-crop.wav")
		(
			ffmpeg
			.input(self.file, ss=self.start_time, to=self.end_time)
			.output(output)
			.global_args('-loglevel', 'error')
			.global_args('-vn')
			.run(overwrite_output=True)
		)
		return output

	def filter_multilingual_subtiles(self, progress_hook=None):
		multi_lingual_subs = []
		for i, sub in enumerate(self.subs_adjusted):
			snippet = self.get_snippet(sub.start, sub.end).export(utils.get_output_path('video_snippet', '.wav'), format="wav").name
			if isnt_target_language(snippet):
				multi_lingual_subs.append(sub)
			progress_hook(i, f"{i}/{len(self.subs_adjusted)}: {sub.text}")
		self.subs_adjusted = multi_lingual_subs
		progress_hook(-1, "done")

	def run_dubbing(self, progress_hook=None):
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
				line = sub.dub_line_ram()
				empty_audio = empty_audio.overlay(line, sub.start*1000)
			except Exception as e:
				print(e)
				total_errors += 1
		self.dub_track = empty_audio.export(utils.get_output_path(self.file, '-dubtrack.wav'), format="wav").name
		progress_hook(i+1, "Mixing New Audio")
		self.mix_av(mixing_ratio=4)
		progress_hook(-1)
		print(f"TOTAL TIME TAKEN: {time.process_time() - operation_start_time}")
		# print(total_errors)

	# This runs an ffmpeg command to combine the audio, video, and subtitles with a specific ratio of how loud to make the dubtrack
	def mix_av(self, mixing_ratio=6, dubtrack=None, output_path=None):
		# i hate python, plz let me use self in func def
		if not dubtrack: dubtrack = self.dub_track
		if not output_path: output_path = utils.get_output_path(self.file, '-dubbed.mkv')

		input_video = ffmpeg.input(self.file)
		input_audio = input_video.audio
		input_wav = ffmpeg.input(dubtrack).audio

		mixed_audio = ffmpeg.filter([input_audio, input_wav], 'amix', duration='first', weights=f"1 {mixing_ratio}")

		output = (
			# input_video['s']
			ffmpeg.output(input_video['v'], mixed_audio, output_path, vcodec="copy", acodec="aac")
			.global_args('-loglevel', 'error')
			.global_args('-shortest')
		)
		ffmpeg.run(output, overwrite_output=True)

	# Change the subs to either a file or a different stream from the video file
	def change_subs(self, stream_index=-1):
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
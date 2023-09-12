"""
The Video class represents a reference to a video from either a file or web link. This class should implement the ncessary info to dub a video.
"""

import ffmpeg
from yt_dlp import YoutubeDL
import utils
from pydub import AudioSegment
from dub_line import load_subs 

class Video:
	def __init__(self, video_URL, loading_progress_hook):
		self.start_time, self.end_time = 0
		self.load_video(video_URL, loading_progress_hook)

	def load_video(self, video_path, progress_hook=None, callback=None):
		self.sub_path = ""
		if video_path.startswith("http"):
			video_path, sub_path = self.download_video(video_path, progress_hook)
		self.file = video_path
		self.subs = self.subs_adjusted = load_subs(sub_path or video_path, utils.get_output_path(self.file, '.srt'))
		self.audio = AudioSegment.from_file(video_path)
		self.total_duration = float(ffmpeg.probe(video_path)["format"]["duration"])
		self.update_time(0, self.total_duration)
		if callback: callback()

	def download_video(self, link, progress_hook=None):
		options = {
			'outtmpl': 'output/download.%(ext)s',
			'writesubtitles': True,
			"subtitlesformat": "srt",
			"progress_hooks": (progress_hook,)
		}
		with YoutubeDL(options) as ydl:
			info = ydl.extract_info(link)
			return ydl.prepare_filename(info), list(info["subtitles"].values())[0][-1]["filepath"]

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
		return [stream for stream in ffmpeg.probe(self.file)["streams"] if stream['codec_type'] != 'attachment']

	def get_snippet(self, start, end):
		return self.audio[start*1000:end*1000]
	
	def crop_audio(file):
		# ffmpeg -i .\saiki.mkv -vn -ss 84 -to 1325 crop.wav
		output = get_output_path(file, "-crop.wav")
		(
			ffmpeg
			.input(file, ss=start_time, to=end_time)
			.output(output)
			.global_args('-loglevel', 'error')
			.global_args('-vn')
			.run(overwrite_output=True)
		)
		return output

	# This runs an ffmpeg command to combine the audio, video, and subtitles with a specific ratio of how loud to make the dubtrack
	def mix_av(self, mixing_ratio=6, dubtrack=None, output_path=None):
		# i hate python, plz let me use self in func def
		if not dubtrack: dubtrack = utils.get_output_path(self.file, '-dubtrack.wav')
		if not output_path: output_path = utils.get_output_path(self.file, '-dubbed.mkv')

		input_video = ffmpeg.input(self.file)
		input_audio = input_video.audio
		input_wav = ffmpeg.input(dubtrack).audio

		mixed_audio = ffmpeg.filter([input_audio, input_wav], 'amix', duration='first', weights=f"1 {mixing_ratio}")

		output = (
			# input_video['s']
			ffmpeg.output(input_video['v'], mixed_audio, output_path, vcodec="copy", acodec="aac")
			.global_args('-shortest')
		)
		ffmpeg.run(output, overwrite_output=True)

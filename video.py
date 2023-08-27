import ffmpeg

class video:
	def __init__(self):
		pass

	def list_streams(self):
		return [stream for stream in ffmpeg.probe(self.file)["streams"] if stream['codec_type'] != 'attachment']

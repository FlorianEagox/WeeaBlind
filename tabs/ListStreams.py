import wx
import app_state
import vocal_isolation
import dub_line
import re
import feature_support
from pydub import AudioSegment
from pydub.playback import play
import utils

if feature_support.ocr_supported:
	import video_ocr
if feature_support.nostril_supported:
	from nostril import nonsense

class ListStreamsTab(wx.Panel):
	def __init__(self, parent, context):
		super().__init__(parent)
		
		self.context = context

		self.scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
		self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
		self.scroll_panel.SetSizer(self.scroll_sizer)
		self.scroll_panel.SetScrollRate(0, 20)
		
		self.rb_audio = wx.RadioBox(self.scroll_panel, majorDimension=1)
		self.rb_subs = wx.RadioBox(self.scroll_panel, majorDimension=1)

		btn_remove_vocals = wx.Button(self, label="Remove vocals")
		btn_remove_vocals.Bind(wx.EVT_BUTTON, self.remove_vocals)
		if not feature_support.vocal_isolation_supported: btn_remove_vocals.Disable()

		btn_ocr = wx.Button(self, label="Extract subs with OCR")
		btn_ocr.Bind(wx.EVT_BUTTON, self.run_ocr)
		if not feature_support.ocr_supported: btn_ocr.Disable()
		lbl_import_external = wx.StaticText(self.scroll_panel, label="Import external Subtitles file")
		self.file_import_external = wx.FilePickerCtrl(self.scroll_panel, message="Import External subtitles file", wildcard="Subtitle Files |*.srt;*.vtt;*.ass")
		self.file_import_external.Bind(wx.EVT_FILEPICKER_CHANGED, self.import_subs)

		box_mixing = wx.StaticBox(self, label="Audio Mixing Settings")
		box_mixing_sizer = wx.StaticBoxSizer(box_mixing)
		box_mixing_grid = wx.GridSizer(2)

		lbl_mixing_ratio = wx.StaticText(self, label="Volume Mixing Ratio")
		self.slider_audio_ratio = wx.Slider(self, value=50)
		self.slider_audio_ratio.Bind(wx.EVT_SLIDER, self.change_mix)
		btn_sample_mix = wx.Button(self, label="Preview Mix")
		btn_sample_mix.Bind(wx.EVT_BUTTON, self.sample_mix)
		
		btn_remix_audio = wx.Button(self, label="Remix Video")
		btn_remix_audio.Bind(wx.EVT_BUTTON, self.remix_audio)

		# Create a sizer for layout
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(btn_remove_vocals, 0, wx.ALL | wx.CENTER, 5)
		sizer.Add(btn_ocr, 0, wx.ALL | wx.CENTER, 5)
		self.scroll_sizer.Add(wx.StaticText(self.scroll_panel, label="Select an Audio Stream:"), 0, wx.ALL, 5)
		self.scroll_sizer.Add(self.rb_audio, 0, wx.ALL | wx.EXPAND, 5)
		self.scroll_sizer.Add(wx.StaticText(self.scroll_panel, label="Select a Subtitle Stream:"), 0, wx.ALL, 5)
		self.scroll_sizer.Add(self.rb_subs, 0, wx.ALL | wx.EXPAND, 5)
		self.scroll_sizer.Add(lbl_import_external, 0, wx.ALL | wx.CENTER, 5)
		self.scroll_sizer.Add(self.file_import_external, 0, wx.ALL | wx.CENTER, 5)
		sizer.Add(self.scroll_panel, 1, wx.SHRINK | wx.ALL | wx.EXPAND | wx.RIGHT, border=10)
		
		box_mixing_grid.Add(lbl_mixing_ratio)
		box_mixing_grid.Add(self.slider_audio_ratio)
		box_mixing_grid.Add(btn_sample_mix)
		box_mixing_grid.Add(btn_remix_audio)
		box_mixing_sizer.Add(box_mixing_grid, 1)
		sizer.Add(box_mixing_sizer, 0, wx.ALIGN_CENTER | wx.SHRINK | wx.ALL, 5)

		self.SetSizer(sizer)



	def populate_streams(self, streams):
		# This code is some of the worst code, i hate it so much, but WX DOESN'T LET ME RESET THE CHOICES LIKE WITH **EVERY** OTHER LIST COMPONENT
		_rb_audio = self.rb_audio
		self.rb_audio = wx.RadioBox(self.scroll_panel,
			choices=[f"Stream #{stream['index']} ({stream.get('tags', {'language': 'unknown'}).get('language', 'unknown')})" for stream in streams["audio"]],
			style=wx.RA_VERTICAL
		)
		self.rb_audio.Bind(wx.EVT_RADIOBOX, lambda a: self.on_audio_selection(None))
		self.scroll_sizer.Replace(_rb_audio, self.rb_audio)
		_rb_audio.Destroy()
		
		if not streams["subs"]:
			self.SetSizerAndFit(self.GetSizer())
			self.Layout()
			return

		_rb_subs_copy = self.rb_subs
		self.rb_subs = wx.RadioBox(self.scroll_panel,
			choices=[f"Stream #{stream['stream']} ({stream['name']})" for stream in streams["subs"]],
			style=wx.RA_VERTICAL
		)
		self.rb_subs.Bind(wx.EVT_RADIOBOX, lambda a: self.on_subtitle_selection(None, streams))
		self.scroll_sizer.Replace(_rb_subs_copy, self.rb_subs)
		_rb_subs_copy.Destroy()
		self.scroll_panel.SetSizerAndFit(self.scroll_sizer)
		self.Fit()
		self.Layout()

	def on_audio_selection(self, event):
		app_state.video.change_audio(self.rb_audio.GetSelection())
		
	def on_subtitle_selection(self, event, streams):
		# app_state.video.change_subs(stream_index=streams['subs'][self.rb_audio.GetSelection()])
		app_state.video.change_subs(stream_index=self.rb_subs.GetSelection())
		self.context.tab_subtitles.create_entries()
	
	def run_ocr(self, event):
		frames = video_ocr.perform_video_ocr(app_state.video.file, sample_rate=1)
		ocr_subs = []
		for index, frame in enumerate(frames):
			try:
				if sum(not char.isspace() for char in frame.text) > 6 and not nonsense(frame.text):
					ocr_subs.append(dub_line.DubbedLine(frame.ts_second, -1, frame.text, index))
			except Exception as e:
					print(e)
		app_state.video.subs_adjusted = ocr_subs
		self.context.tab_subtitles.create_entries()
	
	def remove_vocals(self, event):
		utils.attempt_long_running_task(lambda: vocal_isolation.seperate_file(app_state.video), self, "Spleeter Seperating Vocals", "Attempting to Seperate Vocals with Spleeter")

	def import_subs(self, event):
		app_state.video.change_subs(external_path=self.file_import_external.GetPath())
		self.context.tab_subtitles.create_entries()

	def change_mix(self, event):
		app_state.video.mixing_ratio = self.slider_audio_ratio.GetValue() / 100

	def sample_mix(self, event):
		play(app_state.video.sample_mixing())

	def remix_audio(self, event):
		app_state.video.mix_av(app_state.video.mixing_ratio)
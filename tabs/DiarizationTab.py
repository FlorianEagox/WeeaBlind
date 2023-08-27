import synth
from pydub.playback import play
from pydub import AudioSegment
from pydub import AudioSegment
import synth
import wx

class DiarizationEntry(wx.Panel):
	def __init__(self, parent, context, sub):
		super().__init__(parent)
		self.text = sub.text
		self.sub = sub
		self.start_time = sub.start
		self.end_time = sub.end
		self.speaker = sub.voice
		self.duration = self.end_time - self.start_time
		self.context = context
		
		entry_box = wx.StaticBox(self, label=f"{synth.seconds_to_timecode(self.start_time)} - {synth.seconds_to_timecode(self.end_time)}")
		entry_sizer = wx.StaticBoxSizer(entry_box, wx.VERTICAL)

		text_label = wx.StaticText(self, label=f"Speaker: {self.speaker}\nText: {self.text}")
		entry_sizer.Add(text_label, 0, wx.EXPAND | wx.ALL, border=5)

		playback_button = wx.Button(self, label="Play")
		playback_button.Bind(wx.EVT_BUTTON, self.on_playback_button_click)
		entry_sizer.Add(playback_button, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		sample_button = wx.Button(self, label="Sample")
		sample_button.Bind(wx.EVT_BUTTON, self.on_sample_button_click)
		entry_sizer.Add(sample_button, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		self.SetSizerAndFit(entry_sizer)

	def on_playback_button_click(self, event):
		play(synth.get_snippet(self.start_time, self.end_time))
		pass

	def on_sample_button_click(self, event):
		# sample = synth.dub_line_ram(synth.speakers[self.speaker].speak(self.text, 'output/sample.wav'), self.start_time, self.end_time, self.context.check_match_volume.GetValue())
		play(synth.dub_line_ram(self.sub))

class DiarizationTab(wx.Panel):
	def __init__(self, notebook, context):
		super().__init__(notebook)
		self.context = context
		btn_language_filter = wx.Button(self, label="Filter Language")
		btn_language_filter.Bind(wx.EVT_BUTTON, self.filter_language)
		btn_diarize = wx.Button(self, label="Run Diarization")
		btn_diarize.Bind(wx.EVT_BUTTON, self.run_diarization)
		self.scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
		self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
		self.scroll_panel.SetSizer(self.scroll_sizer)
		self.scroll_panel.SetScrollRate(0, 20)

		# self.create_entries()

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(btn_language_filter, 0, wx.CENTER)
		main_sizer.Add(btn_diarize, 0, wx.CENTER)
		main_sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, border=10)

		self.SetSizerAndFit(main_sizer)

	def run_diarization(self, event):
		synth.run_diarization()
		self.create_entries()
		self.context.update_voices_list()
	
	def filter_language(self, event):
		synth.find_multilingual_subtiles()
		self.create_entries()
		self.context.update_voices_list()

	def create_entries(self):
		self.scroll_sizer.Clear(delete_windows=True)
		rttm_data = synth.subs_adjusted
		for entry in rttm_data:
			# diarization_entry = DiarizationEntry(
			# 	self.scroll_panel,
			# 	start_time=entry[1],
			# 	end_time=entry[2],
			# 	speaker=entry[0],
			# 	text=synth.subs_adjusted[synth.find_nearest([sub.startZ for sub in synth.subs_adjusted], entry[1])].content
			# )
			diarization_entry = DiarizationEntry(
				self.scroll_panel,
				context=self.context,
				sub=entry
			)
			self.scroll_sizer.Add(diarization_entry, 0, wx.EXPAND | wx.ALL, border=5)

		self.Layout()
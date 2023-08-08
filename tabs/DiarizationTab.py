import synth
from pydub.playback import play
from pydub import AudioSegment
import synth
import wx

class DiarizationEntry(wx.Panel):
	def __init__(self, parent, start_time, end_time, speaker, text):
		super().__init__(parent)
		self.text = text
		self.duration = end_time
		entry_box = wx.StaticBox(self, label=f"{start_time:.2f} - {end_time:.2f}")
		entry_sizer = wx.StaticBoxSizer(entry_box, wx.VERTICAL)

		text_label = wx.StaticText(self, label=f"Speaker: {speaker}\nText: {text}")
		entry_sizer.Add(text_label, 0, wx.EXPAND | wx.ALL, border=5)

		playback_button = wx.Button(self, label="Play")
		playback_button.Bind(wx.EVT_BUTTON, self.on_playback_button_click)
		entry_sizer.Add(playback_button, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		sample_button = wx.Button(self, label="Sample")
		sample_button.Bind(wx.EVT_BUTTON, self.on_sample_button_click)
		entry_sizer.Add(sample_button, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		self.SetSizerAndFit(entry_sizer)

	def on_playback_button_click(self, event):
		# Implement playback functionality here
		pass

	def on_sample_button_click(self, event):
		adjustment = synth.adjust_fit_rate(synth.currentSpeaker.speak(self.text, 'output/sample.wav'), self.duration)
		play(AudioSegment.from_file(adjustment))
		pass

class DiarizationTab(wx.Panel):
	def __init__(self, notebook, parent):
		super().__init__(notebook)
		self.parent = parent
		self.scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
		self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
		self.scroll_panel.SetSizer(self.scroll_sizer)
		self.scroll_panel.SetScrollRate(0, 20)  # Add scroll rate (pixels per scroll step)

		self.create_entries()

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, border=10)

		self.SetSizerAndFit(main_sizer)

	def create_entries(self):
		rttm_data = synth.subs_adjusted
		for entry in rttm_data:
			# diarization_entry = DiarizationEntry(
			# 	self.scroll_panel,
			# 	start_time=entry[1],
			# 	end_time=entry[2],
			# 	speaker=entry[0],
			# 	text=synth.subs_adjusted[synth.find_nearest([sub.start.total_seconds() for sub in synth.subs_adjusted], entry[1])].content
			# )
			diarization_entry = DiarizationEntry(
				self.scroll_panel,
				start_time=entry.start.total_seconds(),
				end_time=entry.end.total_seconds() - entry.start.total_seconds(),
				speaker=0,
				text=entry.content # synth.subs_adjusted[synth.find_nearest([sub.start.total_seconds() for sub in synth.subs_adjusted], entry[1])].content
			)
			self.scroll_sizer.Add(diarization_entry, 0, wx.EXPAND | wx.ALL, border=5)

		self.scroll_sizer.Layout()

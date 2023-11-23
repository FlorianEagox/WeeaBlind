import utils
import app_state
from pydub.playback import play
import wx
import threading
import diarize

class SubtitleEntry(wx.Panel):
	def __init__(self, parent, context, sub):
		super().__init__(parent)
		self.text = sub.text
		self.sub = sub
		self.start_time = sub.start
		self.end_time = sub.end
		self.speaker = sub.voice
		self.duration = self.end_time - self.start_time
		self.context = context
		
		entry_box = wx.StaticBox(self, label=f"{utils.seconds_to_timecode(self.start_time)} - {utils.seconds_to_timecode(self.end_time)}")
		entry_sizer = wx.StaticBoxSizer(entry_box, wx.VERTICAL)

		lbl_text = wx.StaticText(self, label=f"Speaker: {self.speaker}\nText: {self.text}")
		entry_sizer.Add(lbl_text, 0, wx.EXPAND | wx.ALL, border=5)

		lbl_language = wx.StaticText(self, label=f"Language: ${sub.language}")
		entry_sizer.Add(lbl_language, 0, border=2)

		btn_playback = wx.Button(self, label="Play")
		btn_playback.Bind(wx.EVT_BUTTON, self.on_playback_button_click)
		entry_sizer.Add(btn_playback, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		btn_sample = wx.Button(self, label="Sample")
		btn_sample.Bind(wx.EVT_BUTTON, self.on_sample_button_click)
		entry_sizer.Add(btn_sample, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		self.SetSizerAndFit(entry_sizer)

	def on_playback_button_click(self, event):
		play(app_state.video.get_snippet(self.start_time, self.end_time))
		pass

	def on_sample_button_click(self, event):
		play(self.sub.dub_line_file(self.context.chk_match_volume.Value))

class SubtitlesTab(wx.Panel):
	def __init__(self, notebook, context):
		super().__init__(notebook)
		self.context = context
		self.subs_displayed = []
		
		lbl_lang_prompt = wx.StaticText(self, label="Remove all subs of this language from dubbing")
		btn_lang_detect = wx.Button(self, label="Run Language Detection")
		btn_lang_detect.Bind(wx.EVT_BUTTON, self.detect_langs)
		btn_language_filter = wx.Button(self, label="Filter Language")
		# btn_language_filter.Bind(wx.EVT_BUTTON, self.filter_language)
		
		btn_diarize = wx.Button(self, label="Run Diarization")
		btn_diarize.Bind(wx.EVT_BUTTON, self.run_diarization)
		
		self.scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
		self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
		self.scroll_panel.SetSizer(self.scroll_sizer)
		self.scroll_panel.SetScrollRate(0, 20)

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(lbl_lang_prompt, 0, wx.CENTER)
		main_sizer.Add(btn_lang_detect, 0, wx.CENTER)
		main_sizer.Add(btn_language_filter, 0, wx.CENTER)
		main_sizer.Add(btn_diarize, 0, wx.CENTER)
		main_sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, border=10)

		self.SetSizerAndFit(main_sizer)

	def run_diarization(self, event):
		diarize.run_diarization(app_state.video)
		self.create_entries()
		self.context.update_voices_list()
	
	def detect_langs(self, event):
		dialog = wx.ProgressDialog("Filtering Subtitles", "starting", len(app_state.video.subs_adjusted), self)
		def update_progress(progress, status):
			def run_after():
				self.create_entries()
				self.context.update_voices_list()
				dialog.Destroy()
			if progress == -1:
				return wx.CallAfter(run_after)
			else:
				wx.CallAfter(dialog.Update, progress, status)
		threading.Thread(target=app_state.video.filter_multilingual_subtiles, args=(update_progress,)).start()

	def filter_language(self, event):
		dialog = wx.ProgressDialog("Filtering Subtitles", "starting", len(app_state.video.subs_adjusted), self)
		def update_progress(progress, status):
			def run_after():
				self.create_entries()
				self.context.update_voices_list()
				dialog.Destroy()
			if progress == -1:
				return wx.CallAfter(run_after)
			else:
				wx.CallAfter(dialog.Update, progress, status)
		threading.Thread(target=app_state.video.filter_multilingual_subtiles, args=(update_progress,)).start()


	def create_entries(self):
		self.scroll_sizer.Clear(delete_windows=True)
		for sub in app_state.video.subs_adjusted: # self.subs_displayed:
			diarization_entry = SubtitleEntry(
				self.scroll_panel,
				context=self.context,
				sub=sub
			)
			self.scroll_sizer.Add(diarization_entry, 0, wx.EXPAND | wx.ALL, border=5)

		self.Layout()
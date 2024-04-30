import utils
import app_state
from pydub.playback import play
import wx
import threading
import diarize
import feature_support

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

		lbl_language = wx.StaticText(self, label=f"Language: {sub.language}")
		entry_sizer.Add(lbl_language, 0, border=2)

		btn_playback = wx.Button(self, label="Play")
		btn_playback.Bind(wx.EVT_BUTTON, self.on_playback_button_click)
		entry_sizer.Add(btn_playback, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		btn_sample = wx.Button(self, label="Sample")
		btn_sample.Bind(wx.EVT_BUTTON, self.on_sample_button_click)
		entry_sizer.Add(btn_sample, 0, wx.ALIGN_LEFT | wx.ALL, border=5)

		self.chk_mark_export = wx.CheckBox(self, label="Select Subtitle")
		entry_sizer.Add(self.chk_mark_export, 0, wx.ALIGN_LEFT)

		self.SetSizerAndFit(entry_sizer)

	def on_playback_button_click(self, event):
		play(app_state.video.get_snippet(self.start_time, self.end_time))
		pass

	def on_sample_button_click(self, event):
		play(self.sub.dub_line_file(match_rate=self.context.chk_match_rate.GetValue())[0])

class SubtitlesTab(wx.Panel):
	def __init__(self, notebook, context):
		super().__init__(notebook)
		self.context = context
		self.subs_displayed = []
		tb_controls = wx.ToolBar(self)
		
		lbl_lang_prompt = wx.StaticText(tb_controls, label="Remove all subs of this language from dubbing")
		btn_lang_detect = wx.Button(tb_controls, label="Run Language Detection")
		btn_lang_detect.Bind(wx.EVT_BUTTON, self.detect_langs)
		btn_language_filter = wx.Button(tb_controls, label="Filter Language")
		btn_language_filter.Bind(wx.EVT_BUTTON, self.remove_langs)
		
		btn_assign_to_voice = wx.Button(tb_controls, label="Assign Selected Voice")
		btn_assign_to_voice.Bind(wx.EVT_BUTTON, self.assign_voice)

		btn_export_clone = wx.Button(tb_controls, label="Export Clone")
		btn_export_clone.Bind(wx.EVT_BUTTON, self.export_clone)
		
		btn_diarize = wx.Button(tb_controls, label="Run Diarization")
		btn_diarize.Bind(wx.EVT_BUTTON, self.run_diarization)
		if not feature_support.diarization_supported: btn_diarize.Disable()
		self.lb_detected_langs = wx.CheckListBox(tb_controls, choices=["en", "es", "jp"])
		if not feature_support.language_detection_supported:
			btn_lang_detect.Disable()
			self.lb_detected_langs.Disable()
			btn_language_filter.Disable()

		self.scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
		self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)
		self.scroll_panel.SetSizer(self.scroll_sizer)
		self.scroll_panel.SetScrollRate(0, 20)
		tb_controls.AddControl(btn_lang_detect)
		tb_controls.AddControl(lbl_lang_prompt)
		tb_controls.AddControl(self.lb_detected_langs)
		tb_controls.AddControl(btn_language_filter)
		tb_controls.AddControl(btn_diarize)
		tb_controls.AddControl(btn_assign_to_voice)
		tb_controls.AddControl(btn_export_clone)
		tb_controls.Realize()

		self.lbl_subs_placecholder = wx.StaticText(self.scroll_panel, label="No Subtitles Loaded")
		self.scroll_sizer.Add(self.lbl_subs_placecholder, 0, wx.CENTER)

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(tb_controls, 0, wx.CENTER)
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
				self.update_langs()
				self.create_entries()
				dialog.Destroy()
			if progress == -1:
				return wx.CallAfter(run_after)
			else:
				wx.CallAfter(dialog.Update, progress, status)
		threading.Thread(target=app_state.video.detect_subs_lang, args=(update_progress, )).start()

	def filter_language(self, event):
		exclusions = self.lb_detected_langs.CheckedStrings
		print("GWEEP", exclusions)
		app_state.video.filter_multilingual_subtiles(exclusions)
		self.update_langs()
		self.create_entries()


	def create_entries(self):
		self.scroll_sizer.Clear(delete_windows=True)
		for sub in app_state.video.subs_adjusted: # self.subs_displayed:
			diarization_entry = SubtitleEntry(
				self.scroll_panel,
				context=self.context,
				sub=sub
			)
			diarization_entry.SetRefData
			self.scroll_sizer.Add(diarization_entry, 0, wx.EXPAND | wx.ALL, border=5)

		self.Layout()

	def update_langs(self):
		self.lb_detected_langs.Clear()
		self.lb_detected_langs.AppendItems(sorted(list(set(sub.language for sub in app_state.video.subs_adjusted))))
		self.Layout()

	def remove_langs(self, event):
		# maybe move this into the video class?
		app_state.video.subs_adjusted = [sub for sub in app_state.video.subs_adjusted if not sub.language in self.lb_detected_langs.GetCheckedStrings()]
		self.update_langs()
		self.create_entries()
	
	def assign_voice(self, event):
		[child.GetWindow().sub.update_voice(self.context.lb_voices.GetSelection()) for child in self.scroll_sizer.GetChildren() if child.GetWindow().chk_mark_export.IsChecked()],
		self.create_entries()

	def export_clone(self, event):
		dlg_save = wx.FileDialog(self, "Save a new clone sample", "./output", "voice_sample.wav", "*.wav", wx.FD_SAVE)
		if dlg_save.ShowModal() == wx.ID_OK:
			app_state.video.export_clone(
				[child.GetWindow().sub for child in self.scroll_sizer.GetChildren() if child.GetWindow().chk_mark_export.IsChecked()],
				dlg_save.GetPath()
			)
		dlg_save.Destroy()

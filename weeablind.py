import wx
import wx.adv
import sys
from tabs.ConfigureVoiceTab import ConfigureVoiceTab
from tabs.SubtitlesTab import SubtitlesTab
from tabs.ListStreams import ListStreamsTab
from tabs.GreeterView import GreeterView
import threading
import utils
from video import Video
import app_state
import feature_support
from Voice import Voice
import os

class GUI(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		
		lbl_title = wx.StaticText(self, label="WeeaBlind")
		lbl_GPU = wx.StaticText(self, label=f"GPU Detected? {feature_support.gpu_supported}")
		lbl_GPU.SetForegroundColour((0, 255, 0) if feature_support.gpu_supported else (255, 0, 0))


		btn_choose_file = wx.Button(self, label="Choose File")
		btn_choose_file.Bind(wx.EVT_BUTTON, self.open_file)

		lbl_main_file = wx.StaticText(self, label="Choose a video file or link to a YouTube video:")
		self.txt_main_file = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.test_video_name)
		self.txt_main_file.Bind(wx.EVT_TEXT_ENTER, lambda event: self.load_video(self.txt_main_file.Value))
		lbl_dl_lang = wx.StaticText(self, label="Download subtitle language:")
		self.txt_dl_lang = wx.TextCtrl(self, value="en")

		lbl_start_time = wx.StaticText(self, label="Start Time:")
		lbl_end_time = wx.StaticText(self, label="End Time:")
		self.txt_start = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.seconds_to_timecode(0))
		self.txt_end = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.seconds_to_timecode(0))
		self.txt_start.Bind(wx.EVT_TEXT_ENTER, self.change_crop_time)
		self.txt_end.Bind(wx.EVT_TEXT_ENTER, self.change_crop_time)

		self.chk_match_rate = wx.CheckBox(self, label="Match Speaker Rate")
		self.chk_match_rate.SetValue(True)

		self.lb_voices = wx.ListBox(self, choices=[speaker.name for speaker in app_state.speakers])
		self.lb_voices.Bind(wx.EVT_LISTBOX, self.on_voice_change)
		self.lb_voices.Select(0)

		btn_new_speaker = wx.Button(self, label="New Speaker")
		btn_new_speaker.Bind(wx.EVT_BUTTON, self.add_speaker)

		tab_control = wx.Notebook(self)
		tab_control.AddPage(GreeterView(tab_control, self), "Welcome!")
		self.tab_voice_config = ConfigureVoiceTab(tab_control, self)
		tab_control.AddPage(self.tab_voice_config, "Configure Voices")
		self.tab_subtitles = SubtitlesTab(tab_control, self)
		tab_control.AddPage(self.tab_subtitles, "Subtitles")
		self.streams_tab = ListStreamsTab(tab_control, self)
		tab_control.AddPage(self.streams_tab, "Video Streams")
		
		btn_run_dub = wx.Button(self, label="Run Dubbing!")
		btn_run_dub.Bind(wx.EVT_BUTTON, self.run_dub)
		
		sizer = wx.GridBagSizer(vgap=5, hgap=5)
		sizer.Add(lbl_title, pos=(0, 0), span=(1, 2), flag=wx.CENTER | wx.ALL, border=5)
		sizer.Add(lbl_GPU, pos=(0, 3), span=(1, 1), flag=wx.CENTER | wx.ALL, border=5)
		sizer.Add(lbl_main_file, pos=(2, 0), span=(1, 2), flag=wx.LEFT | wx.TOP, border=5)
		sizer.Add(self.txt_main_file, pos=(3, 0), span=(1, 2), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
		sizer.Add(btn_choose_file, pos=(3, 2), span=(1, 1), flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=5)
		sizer.Add(lbl_dl_lang, pos=(4, 0), span=(1,1), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
		sizer.Add(self.txt_dl_lang, pos=(4, 1), span=(1,1), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
		sizer.Add(lbl_start_time, pos=(5, 0), flag=wx.LEFT | wx.TOP, border=3)
		sizer.Add(self.txt_start, pos=(5, 1), flag= wx.TOP | wx.RIGHT, border=3)
		sizer.Add(lbl_end_time, pos=(5, 2), flag=wx.LEFT | wx.TOP, border=3)
		sizer.Add(self.txt_end, pos=(5, 3), flag= wx.TOP | wx.RIGHT, border=3)
		sizer.Add(self.chk_match_rate, pos=(6, 0), span=(1, 2), flag=wx.LEFT | wx.TOP, border=5)
		sizer.Add(self.lb_voices, pos=(7, 0), span=(2, 1), flag=wx.EXPAND | wx.LEFT | wx.TOP, border=5)
		sizer.Add(btn_new_speaker, pos=(9, 0), span=(1, 1), flag=wx.LEFT, border=5)
		sizer.Add(tab_control, pos=(7, 1), span=(2, 3), flag=wx.SHRINK | wx.ALL, border=5)
		sizer.Add(btn_run_dub, pos=(10, 2), span=(1, 1), flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=5)
		# sizer.AddGrowableCol(1)
		# sizer.AddGrowableRow(7)
		self.tab_voice_config.update_voice_fields(None)

		self.SetSizerAndFit(sizer)
		wx.CallAfter(self.check_ffmpeg)

	def check_ffmpeg(self):
		if not feature_support.ffmpeg_supported:
			msg_has_ffmpeg = wx.MessageDialog(self, "FFmpeg is not detected on your system, Would you like to automatically install it?", "Install FFmpeg?", style=wx.YES_NO | wx.ICON_QUESTION)
			if msg_has_ffmpeg.ShowModal() == wx.ID_YES:
				msg_loading = wx.ProgressDialog("Installing FFmpeg...", "Installing FFmpeg", parent=self, style=wx.PD_AUTO_HIDE | wx.PD_SMOOTH)
				msg_loading.Update(1)
				try:
					feature_support.install_ffmpeg()
				except Exception as e:
					print(e)
					wx.MessageBox(f"Installing FFmpeg failed, please install it manually, and add it to your system envionrment path.\n\n{e}", "FFmpeg Install failed", wx.ICON_ERROR, self)
				msg_loading.Destroy()
  

	def open_file(self, evenet):
		dlg = wx.FileDialog(
			frame, message="Choose a file",
			wildcard="*.*",
			style=wx.FD_OPEN | wx.FD_CHANGE_DIR
		)
		if dlg.ShowModal() == wx.ID_OK:
			self.load_video(dlg.GetPath())
		dlg.Destroy()

	def load_video(self, video_path):
		def update_ui():
			self.txt_main_file.Value = app_state.video.file
			self.txt_start.SetValue(utils.seconds_to_timecode(app_state.video.start_time))
			self.txt_end.SetValue(utils.seconds_to_timecode(app_state.video.end_time))
			self.tab_subtitles.create_entries()

		def initialize_video(progress=True):
			app_state.video = Video(video_path, update_progress if progress else print, lang=self.txt_dl_lang.Value)
			wx.CallAfter(update_ui)
			wx.CallAfter(self.streams_tab.populate_streams, app_state.video.list_streams())

		if video_path.startswith("http"):
			dialog = wx.ProgressDialog("Downloading Video", "Download starting", 100, self)

			def update_progress(progress=None):
				status = progress['status'] if progress else "waiting"
				total = progress.get("fragment_count", progress.get("total_bytes", 0))
				if status == "downloading" and total:
					completed = progress.get("fragment_index", progress.get("downloaded_bytes", 1))
					percent_complete = int(100 * (completed / total))
					wx.CallAfter(dialog.Update, percent_complete, f"{status}: {percent_complete}% \n {progress['info_dict'].get('fulltitle', '')}")
				elif status == "complete":
					if dialog:
						wx.CallAfter(dialog.Destroy)
				elif status == "error":
					wx.CallAfter(wx.MessageBox,
						f"Failed to download video with the following Error:\n {str(progress['error'])}",
						"Error",
						wx.ICON_ERROR
					)
					update_progress({"status": "complete"})

			threading.Thread(target=initialize_video).start()
		else:
			initialize_video(False)

	def change_crop_time(self, event):
		app_state.video.update_time(
			utils.timecode_to_seconds(self.txt_start.Value),
			utils.timecode_to_seconds(self.txt_end.Value)
		)
		self.tab_subtitles.create_entries()

	def update_voices_list(self):
		self.lb_voices.Set([speaker.name for speaker in app_state.speakers])
		self.lb_voices.Select(self.lb_voices.Strings.index(app_state.current_speaker.name))

	def on_voice_change(self, event):
		app_state.current_speaker = app_state.speakers[self.lb_voices.GetSelection()]
		app_state.sample_speaker = app_state.current_speaker
		self.tab_voice_config.update_voice_fields(event)

	def add_speaker(self, event):
		num_voice = self.lb_voices.GetCount()
		app_state.speakers.append(Voice(Voice.VoiceType.SYSTEM, name=f"Voice {num_voice}"))
		self.update_voices_list()
		self.lb_voices.Select(num_voice)

	def run_dub(self, event):
		progress_dialog = wx.ProgressDialog(
			"Dubbing Progress",
			"Starting...",
			maximum=len(app_state.video.subs_adjusted) + 1,  # +1 for combining phase
			parent=self,
			style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
		)
		dub_thread = None
		def update_progress(i, text=""):
			if i == -1:
				return wx.CallAfter(progress_dialog.Destroy)
			wx.CallAfter(progress_dialog.Update, i, text)

		dub_thread = threading.Thread(target=app_state.video.run_dubbing, args=(update_progress,self.chk_match_rate.GetValue()))
		dub_thread.start()

if __name__ == '__main__':
	utils.create_output_dir()
	app = wx.App(False)
	frame = wx.Frame(None, wx.ID_ANY, utils.APP_NAME, size=(1270, 800))
	frame.Center()
	icon_path = "logo.ico" if not utils.is_deployed else os.path.join('_internal', 'logo.ico')
	frame.SetIcon(wx.Icon(os.path.abspath(icon_path), wx.BITMAP_TYPE_ANY))
	gui = GUI(frame)
	frame.Show()
	app.MainLoop()

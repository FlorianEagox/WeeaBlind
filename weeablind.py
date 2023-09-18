import wx
import wx.adv
from Voice import Voice
from pydub import AudioSegment
from pydub.playback import play
from tabs.ConfigureVoiceTab import ConfigureVoiceTab
from tabs.SubtitlesTab import SubtitlesTab
from tabs.ListStreams import ListStreamsTab
import threading
import utils
from video import Video
import app_state
from video import Video
import json

class GUI(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		# Labels
		lbl_title = wx.StaticText(self, label="WeeaBlind")
		lbl_GPU = wx.StaticText(self, label=f"GPU Detected? {utils.gpu_detected}")
		lbl_GPU.SetForegroundColour((0, 255, 0) if utils.gpu_detected else (255, 0, 0))
		lbl_main_file = wx.StaticText(self, label="Choose a video file or link to a YouTube video:")
		lbl_start_time = wx.StaticText(self, label="Start Time:")
		lbl_end_time = wx.StaticText(self, label="End Time:")

		# Controls
		btn_choose_file = wx.Button(self, label="Choose File")
		btn_choose_file.Bind(wx.EVT_BUTTON, self.open_file)

		self.txt_main_file = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.test_video_name)
		self.txt_main_file.Bind(wx.EVT_TEXT_ENTER, lambda event: self.load_video(self.txt_main_file.Value))

		self.txt_start = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.seconds_to_timecode(0))
		self.txt_end = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.seconds_to_timecode(0))
		self.txt_start.Bind(wx.EVT_TEXT_ENTER, self.change_crop_time)
		self.txt_end.Bind(wx.EVT_TEXT_ENTER, self.change_crop_time)

		self.chk_match_volume = wx.CheckBox(self, label="Match Speaker Volume")
		self.chk_match_volume.SetValue(True)

		self.lb_voices = wx.ListBox(self, choices=[speaker.name for speaker in app_state.speakers])
		self.lb_voices.Bind(wx.EVT_LISTBOX, self.on_voice_change)
		self.lb_voices.Select(0)

		tab_control = wx.Notebook(self)
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
		sizer.Add(lbl_start_time, pos=(4, 0), flag=wx.LEFT | wx.TOP, border=5)
		sizer.Add(self.txt_start, pos=(4, 1), flag= wx.TOP | wx.RIGHT, border=5)
		sizer.Add(lbl_end_time, pos=(5, 0), flag=wx.LEFT | wx.TOP, border=5)
		sizer.Add(self.txt_end, pos=(5, 1), flag= wx.TOP | wx.RIGHT, border=5)
		sizer.Add(self.chk_match_volume, pos=(6, 0), span=(1, 2), flag=wx.LEFT | wx.TOP, border=5)
		sizer.Add(self.lb_voices, pos=(7, 0), span=(1, 1), flag=wx.EXPAND | wx.LEFT | wx.TOP, border=5)
		sizer.Add(tab_control, pos=(7, 1), span=(1, 3), flag=wx.EXPAND | wx.ALL, border=5)
		sizer.Add(btn_run_dub, pos=(9, 2), span=(1, 1), flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=5)
		sizer.AddGrowableCol(1)
		self.tab_voice_config.update_voice_fields(None)

		self.SetSizerAndFit(sizer)

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
			app_state.video = Video(video_path, update_progress if progress else print)
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

		dub_thread = threading.Thread(target=app_state.video.run_dubbing, args=(update_progress,))
		dub_thread.start()

if __name__ == '__main__':
	utils.create_output_dir()
	app = wx.App(False)
	frame = wx.Frame(None, wx.ID_ANY, utils.APP_NAME, size=(800, 800))
	frame.Center()
	gui = GUI(frame)
	frame.Show()
	app.MainLoop()

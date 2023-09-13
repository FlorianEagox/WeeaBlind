import wx
from Voice import Voice
from pydub import AudioSegment
from pydub.playback import play
from tabs.ConfigureVoiceTab import ConfigureVoiceTab
from tabs.DiarizationTab import DiarizationTab
import threading
import utils
from video import Video
import app_state
from video import Video

class GUI(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		btn_choose_file = wx.Button(self, label="Choose FIle")
		btn_choose_file.Bind(wx.EVT_BUTTON, self.open_file)

		self.txt_main_file = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.test_video_name)
		self.txt_main_file.Bind(wx.EVT_TEXT_ENTER, lambda event: self.load_video(self.txt_main_file.Value))
		lbl_title = wx.StaticText(self, label="WeeaBlind")

		lbl_GPU = wx.StaticText(self, label=f"GPU Detected? {utils.gpu_detected}")
		lbl_GPU.SetForegroundColour((0, 255, 0) if utils.gpu_detected else (255, 0, 0))

		self.chk_match_volume = wx.CheckBox(self, label="Match Speaker Volume")
		self.chk_match_volume.SetValue(True)
		
		self.txt_start = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.seconds_to_timecode(0))
		self.txt_end   = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, value=utils.seconds_to_timecode(0))
		self.txt_start.Bind(wx.EVT_TEXT_ENTER, self.change_crop_time)
		self.txt_end.Bind(wx.EVT_TEXT_ENTER, self.change_crop_time)

		self.chk_multilangual = wx.CheckBox(self)

		# SHOW A LIST OF VOICES
		self.lb_voices = wx.ListBox(self, choices=[speaker.name for speaker in app_state.speakers])
		self.lb_voices.Bind(wx.EVT_LISTBOX, self.on_voice_change)
		self.lb_voices.Select(0)

		tab_control = wx.Notebook(self)
		self.tab_voice_config = ConfigureVoiceTab(tab_control, self)
		tab_control.AddPage(self.tab_voice_config, "Configure Voices")
		self.tab_diarization = DiarizationTab(tab_control, self)
		tab_control.AddPage(self.tab_diarization, "Diarization")

		btn_run_dub = wx.Button(self, label="Run Dubbing!")
		btn_run_dub.Bind(wx.EVT_BUTTON, self.run_dub)

		self.on_voice_change(None)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(lbl_title, 0, wx.ALL|wx.CENTER, 5)
		sizer.Add(lbl_GPU, 0, wx.ALL|wx.CENTER, 5)
		sizer.Add(self.txt_main_file, 0, wx.ALL|wx.EXPAND, 5)
		sizer.Add(btn_choose_file, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		sizer.Add(self.txt_start, 0, wx.ALL, 5)
		sizer.Add(self.txt_end, 0, wx.ALL, 5)
		sizer.Add(self.chk_match_volume, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		sizer.Add(self.lb_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		sizer.Add(tab_control, 1, wx.EXPAND, 5)
		sizer.Add(btn_run_dub, 1, wx.ALIGN_RIGHT, 5)
		self.SetSizer(sizer)

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
			self.tab_diarization.create_entries()
		if video_path.startswith("http"):
			dialog = wx.ProgressDialog("Downloading Vidoe", "download starting", 100, self)
			def update_progress(progress=None, finished=False):
				if finished:
					wx.CallAfter(dialog.Destroy)
					wx.CallAfter(update_ui)
					return
				status = progress['status']
				if status == "downloading" and progress["total_bytes"]:
					percent_complete = int(100*(progress["downloaded_bytes"] / progress["total_bytes"]))
					wx.CallAfter(dialog.Update, percent_complete, f"{status}: {percent_complete}% \n {progress['info_dict']['fulltitle'] or ''}")
			
			#python is stupid and won't let you do this as a lambda -_-
			def initialize_video(): app_state.video = Video(video_path, update_progress)
			download_thread = threading.Thread(target=initialize_video)
			download_thread.start()
		else:
			app_state.video = Video(video_path)
			update_ui()
		

	def change_crop_time(self, event):
		app_state.video.update_time(
			utils.timecode_to_seconds(self.txt_start.Value),
			utils.timecode_to_seconds(self.txt_end.Value)
		)
		self.tab_diarization.create_entries()

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

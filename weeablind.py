import wx
import synth
from Voice import Voice
from torch.cuda import is_available
from pydub import AudioSegment
from pydub.playback import play
from tabs.ConfigureVoiceTab import ConfigureVoiceTab
from tabs.DiarizationTab import DiarizationTab

app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "WeeaBlind", size=(800, 800))
frame.Center()

class GUI(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		btn_choose_file = wx.Button(self, label="Choose FIle")
		btn_choose_file.Bind(wx.EVT_BUTTON, self.open_file)

		self.txt_main_file = wx.TextCtrl(self, wx.TC_LEFT, synth.test_video_name)
		lbl_title = wx.StaticText(self, label="WeeaBlind")

		lbl_GPU = wx.StaticText(self, label=f"GPU Detected? {is_available()}")
		lbl_GPU.SetForegroundColour((0, 255, 0) if is_available() else (255, 0, 0))

		# SHOW A LIST OF VOICES
		self.lb_voices = wx.ListBox(self, choices=[speaker.name for speaker in synth.speakers])
		self.lb_voices.Bind(wx.EVT_LISTBOX, self.on_voice_change)
		self.lb_voices.Select(0)

		tab_control = wx.Notebook(self)
		self.tab_voice_config = ConfigureVoiceTab(tab_control, self)
		tab_control.AddPage(self.tab_voice_config, "Configure Voices")
		tab_diarization = DiarizationTab(tab_control, self)
		tab_control.AddPage(tab_diarization, "Diarization")

		self.on_voice_change(None)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(lbl_title, 0, wx.ALL|wx.CENTER, 5)
		sizer.Add(lbl_GPU, 0, wx.ALL|wx.CENTER, 5)
		sizer.Add(self.txt_main_file, 0, wx.ALL|wx.EXPAND, 5)
		sizer.Add(btn_choose_file, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		sizer.Add(self.lb_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		sizer.Add(tab_control, 1, wx.EXPAND, 5)

		self.SetSizer(sizer)

	def open_file(self, evenet):
			dlg = wx.FileDialog(
				frame, message="Choose a file",
				wildcard="*.*",
				style=wx.FD_OPEN | wx.FD_CHANGE_DIR
			)
			if dlg.ShowModal() == wx.ID_OK:
				self.txt_main_file.Value = dlg.GetPath()
			dlg.Destroy()

	def update_voices_list(self):
		self.lb_voices.Set([speaker.name for speaker in synth.speakers])
		self.lb_voices.Select(self.lb_voices.Strings.index(synth.currentSpeaker.name))

	def on_voice_change(self, event):
		synth.currentSpeaker = synth.speakers[self.lb_voices.GetSelection()]
		synth.sampleSpeaker = synth.currentSpeaker
		self.tab_voice_config.update_voice_fields(event)

gui = GUI(frame)
frame.Show()
app.MainLoop()

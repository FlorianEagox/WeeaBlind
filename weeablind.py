import wx
import synth
from Voice import Voice
from torch.cuda import is_available
from pydub import AudioSegment
from pydub.playback import play

app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "WeeaBlind", size=(800, 800))
frame.Center

currentSpeaker = synth.speakers[0]
sampleSpeaker = currentSpeaker

def open_file(evenet):
		dlg = wx.FileDialog(
			frame, message="Choose a file",
			wildcard="*.*",
			style=wx.FD_OPEN | wx.FD_CHANGE_DIR
		)
		if dlg.ShowModal() == wx.ID_OK:
			txt_main_file.Value = dlg.GetPath()
		dlg.Destroy()


def update_voices_list():
	lb_voices.Set([speaker.name for speaker in synth.speakers])

def on_voice_change(event):
	global currentSpeaker, sampleSpeaker # This is bad, I have no idea why it's not recognized?
	currentSpeaker = synth.speakers[lb_voices.GetSelection()]
	sampleSpeaker = currentSpeaker
	tab_voice_config.update_voice_fields(event)


class ConfigureVoiceTab(wx.Panel):
	def __init__(self, parent):
		super().__init__(parent)

		# EDIT VOICE PARAMS
		lbl_voice_name = wx.StaticText(self, label="Name")
		self.txt_voice_name = wx.TextCtrl(self, value=currentSpeaker.name)
		self.cb_voice_types = wx.ComboBox(self, style= wx.CB_READONLY, choices=[str(val) for val in Voice.VoiceType])
		self.cb_voice_types.Bind(wx.EVT_COMBOBOX, self.change_voice_type)
		self.cb_voice_options = wx.ComboBox(self, style= wx.CB_READONLY, choices=currentSpeaker.list_voice_options())
		self.cb_voice_options.Bind(wx.EVT_COMBOBOX, self.change_voice_params)

		# Show a dropdown box for multi-speaker Coqui models
		self.cb_speaker_voices = wx.ComboBox(self, style=wx.CB_READONLY, choices=[])
		self.cb_speaker_voices.Bind(wx.EVT_COMBOBOX, self.change_voice_params)
		self.cb_speaker_voices.Hide()  # Hide by default, show only when multi-speaker Coqui model is selected

		# SAMPLE CURRENT VOICE
		self.txt_sample_synth = wx.TextCtrl(self, value=f"I do be slurpin' that cheese without my momma's permission")
		self.btn_sample = wx.Button(self, label="Sample Voice")
		self.btn_sample.Bind(wx.EVT_BUTTON, self.sample)

		self.btn_update_voice = wx.Button(self, label="Update Voice")
		self.btn_update_voice.Bind(wx.EVT_BUTTON, self.update_voice)

		szr_voice_params = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(szr_voice_params)

		szr_voice_params.Add(lbl_voice_name, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.txt_voice_name, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.cb_voice_types, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.cb_voice_options, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.cb_speaker_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.txt_sample_synth, 0, wx.ALL|wx.EXPAND, 5)
		szr_voice_params.Add(self.btn_sample, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		szr_voice_params.Add(self.btn_update_voice, 0, wx.ALL|wx.ALIGN_LEFT, 5)


	def sample(self, event):
		output = "output/sample.wav"
		sampleSpeaker.speak(self.txt_sample_synth.Value, output)
		play(AudioSegment.from_file(output))

	def update_voice(self, event):
		global currentSpeaker, sampleSpeaker
		sampleSpeaker.name = self.txt_voice_name.Value
		synth.speakers[synth.speakers.index(currentSpeaker)] = sampleSpeaker
		currentSpeaker = sampleSpeaker
		update_voices_list()

	def show_multispeaker(self):
		if sampleSpeaker.voice_type == Voice.VoiceType.COQUI and sampleSpeaker.is_multispeaker:
			self.cb_speaker_voices.Show()
			self.cb_speaker_voices.Set(sampleSpeaker.list_speakers())
			self.cb_speaker_voices.SetValue(sampleSpeaker.speaker)
		else:
			cb_speaker_voices.Hide()
		panel.Layout()

	def update_voice_fields(self, event):
		self.txt_voice_name.Value = currentSpeaker.name
		self.cb_voice_types.Select(list(Voice.VoiceType.__members__.values()).index(sampleSpeaker.voice_type))
		self.cb_voice_options.Set(sampleSpeaker.list_voice_options())
		self.cb_voice_options.Select(sampleSpeaker.list_voice_options().index(currentSpeaker.voice_option))
		self.show_multispeaker()

	def change_voice_type(self, event):
		global sampleSpeaker
		sampleSpeaker = Voice(list(Voice.VoiceType.__members__.values())[cb_voice_types.GetSelection()])
		self.update_voice_fields(event)

	def change_voice_params(self, event):
		sampleSpeaker.set_voice_params(self.cb_voice_options.GetStringSelection())
		if sampleSpeaker.voice_type == Voice.VoiceType.COQUI and sampleSpeaker.is_multispeaker:
			sampleSpeaker.set_voice_params(speaker=cb_speaker_voices.GetStringSelection())
		else:
			sampleSpeaker.set_voice_params(speaker=None)
		self.show_multispeaker()

panel = wx.Panel(frame)
btn_choose_file = wx.Button(panel, label="Choose FIle")
btn_choose_file.Bind(wx.EVT_BUTTON, open_file)

txt_main_file = wx.TextCtrl(panel, wx.TC_LEFT, "saiki.mkv")
lbl_title = wx.StaticText(panel, label="WeeaBlind")

lbl_GPU = wx.StaticText(panel, label=f"GPU Detected? {is_available()}")
lbl_GPU.SetForegroundColour((0, 255, 0) if is_available() else (255, 0, 0))

# SHOW A LIST OF VOICES
lb_voices = wx.ListBox(panel, choices=[speaker.name for speaker in synth.speakers])
lb_voices.Bind(wx.EVT_LISTBOX, on_voice_change)
lb_voices.Select(0)

tab_control = wx.Notebook(panel)
tab_voice_config = ConfigureVoiceTab(tab_control)
tab_control.AddPage(tab_voice_config, "Configure Voices")


on_voice_change(None)

sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(lbl_title, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(lbl_GPU, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(txt_main_file, 0, wx.ALL|wx.EXPAND, 5)
sizer.Add(btn_choose_file, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
sizer.Add(lb_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
sizer.Add(tab_control, 1, wx.EXPAND, 5)


panel.SetSizer(sizer)

frame.Show()
app.MainLoop()

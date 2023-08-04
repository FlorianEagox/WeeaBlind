import wx
import synth
from Voice import Voice
from torch.cuda import is_available

app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "WeeaBlind", size=(800, 600))
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

def sample(event):
	sampleSpeaker.speak(txt_sample_synth.Value, "output/sample.wav")

def update_voices_list():
	lb_voices.Set([speaker.name for speaker in synth.speakers])

def update_voice(event):
	global currentSpeaker
	currentSpeaker = sampleSpeaker
	currentSpeaker.name = txt_voice_name.Value
	update_voices_list()

def update_voice_fields(event):
	txt_voice_name.Value = currentSpeaker.name
	cb_voice_types.Select(list(Voice.VoiceType.__members__.values()).index(sampleSpeaker.voice_type))
	print('meep')

def on_voice_change(event):
	global currentSpeaker, sampleSpeaker # This is bad, I have no idea why it's not recognized?
	currentSpeaker = synth.speakers[lb_voices.GetSelection()]
	sampleSpeaker = currentSpeaker
	update_voice_fields(event)

def change_voice_type(event):
	global sampleSpeaker
	sampleSpeaker = Voice(list(Voice.VoiceType.__members__.values())[cb_voice_types.GetSelection()])
	cb_voice_options.Set(sampleSpeaker.list_voice_options())

def change_voice_params(event):
	sampleSpeaker.set_voice_params(cb_voice_options.GetStringSelection())

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

# EDIT VOICE PARAMS
lbl_voice_name = wx.StaticText(panel, label="Name")
cb_voice_types = wx.ComboBox(panel, style= wx.CB_READONLY, choices=[str(val) for val in Voice.VoiceType])
cb_voice_types.Bind(wx.EVT_COMBOBOX, change_voice_type)
cb_voice_options = wx.ComboBox(panel, style= wx.CB_READONLY, choices=currentSpeaker.list_voice_options())
cb_voice_options.Bind(wx.EVT_COMBOBOX, change_voice_params)

# SAMPLE CURRENT VOICE
txt_voice_name = wx.TextCtrl(panel, value=currentSpeaker.name)
txt_sample_synth = wx.TextCtrl(panel, value=f"I do be slurpin' that cheese without my momma's permission")
btn_sample = wx.Button(panel, label="Sample Voice")
btn_sample.Bind(wx.EVT_BUTTON, sample)

btn_update_voice = wx.Button(panel, label="Update Voice")
btn_update_voice.Bind(wx.EVT_BUTTON, update_voice)


on_voice_change(None)

sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(lbl_title, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(lbl_GPU, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(txt_main_file, 0, wx.ALL|wx.EXPAND, 5)
sizer.Add(btn_choose_file, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
sizer.Add(lb_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
szr_voice_params = wx.BoxSizer(wx.VERTICAL)
szr_voice_params.Add(lbl_voice_name, 0, wx.ALL|wx.ALIGN_LEFT, 5)
szr_voice_params.Add(txt_voice_name, 0, wx.ALL|wx.ALIGN_LEFT, 5)
szr_voice_params.Add(cb_voice_types, 0, wx.ALL|wx.ALIGN_LEFT, 5)
szr_voice_params.Add(cb_voice_options, 0, wx.ALL|wx.ALIGN_LEFT, 5)
szr_voice_params.Add(txt_sample_synth, 0, wx.ALL|wx.EXPAND, 5)
szr_voice_params.Add(btn_sample, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
szr_voice_params.Add(btn_update_voice, 0, wx.ALL|wx.ALIGN_LEFT, 5)

sizer.Add(szr_voice_params, 1, wx.EXPAND, 5)

panel.SetSizer(sizer)

frame.Show()
app.MainLoop()

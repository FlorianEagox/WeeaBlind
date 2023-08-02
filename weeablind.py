import wx
import synth
from Voice import Voice


app = wx.App(False)
frame = wx.Frame(None, wx.ID_ANY, "WeeaBlind", size=(500, 400))

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
	synth.speakers[lb_voices.GetSelection()].speak(txt_sample_synth.Value, "output/sample.wav")

def update_voices_list():
	lb_voices.Set([speaker.name for speaker in synth.speakers])

def update_voice(event):
	synth.speakers[lb_voices.GetSelection()].name = txt_voice_name.Value
	update_voices_list()

def update_voice_fields(event):
	txt_voice_name.Value = synth.speakers[lb_voices.GetSelection()].name
	print("UPDATING")

panel = wx.Panel(frame)
btn_choose_file = wx.Button(panel, label="Choose FIle")
btn_choose_file.Bind(wx.EVT_BUTTON, open_file)

txt_main_file = wx.TextCtrl(panel, wx.TC_LEFT, "saiki.mkv")
lbl_title = wx.StaticText(panel, label="WeeaBlind")

lb_voices = wx.ListBox(panel, choices=[speaker.name for speaker in synth.speakers])
lb_voices.Select(0)
lb_voices.Bind(wx.EVT_LISTBOX, update_voice_fields)

lbl_voice_name = wx.StaticText(panel, label="Name")
txt_voice_name = wx.TextCtrl(panel, value=lb_voices.GetString(lb_voices.GetSelection()))
txt_sample_synth = wx.TextCtrl(panel, value=f"I do be slurpin' that cheese without my momma's permission")
btn_update_voice = wx.Button(panel, label="Update Voice")
btn_update_voice.Bind(wx.EVT_BUTTON, update_voice)
btn_sample = wx.Button(panel, label="Sample Voice")
btn_sample.Bind(wx.EVT_BUTTON, sample)
cb_voice_types = wx.ComboBox(panel, style= wx.CB_READONLY, choices=[str(val) for val in Voice.VoiceType])


sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(lbl_title, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(txt_main_file, 0, wx.ALL|wx.EXPAND, 5)
sizer.Add(btn_choose_file, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
sizer.Add(lb_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
sizer.Add(lbl_voice_name, 0, wx.ALL|wx.ALIGN_LEFT, 5)
sizer.Add(txt_voice_name, 0, wx.ALL|wx.ALIGN_LEFT, 5)
sizer.Add(txt_sample_synth, 0, wx.ALL|wx.ALIGN_LEFT, 5)
sizer.Add(cb_voice_types, 0, wx.ALL|wx.ALIGN_LEFT, 5)
sizer.Add(btn_sample, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
sizer.Add(btn_update_voice, 0, wx.ALL|wx.ALIGN_LEFT, 5)

panel.SetSizer(sizer)

frame.Show()
app.MainLoop()

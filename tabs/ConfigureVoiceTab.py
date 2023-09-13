import app_state
import wx
from Voice import Voice
import utils

class ConfigureVoiceTab(wx.Panel):
	def __init__(self, notebook, parent):
		super().__init__(notebook)
		self.parent = parent
		# EDIT VOICE PARAMS
		lbl_voice_name = wx.StaticText(self, label="Name")
		self.txt_voice_name = wx.TextCtrl(self, value=app_state.current_speaker.name)
		self.cb_tts_engines = wx.ComboBox(self, style= wx.CB_READONLY, choices=[str(val) for val in Voice.VoiceType])
		self.cb_tts_engines.Bind(wx.EVT_COMBOBOX, self.change_tts_engine)
		self.cb_model_options = wx.ComboBox(self, style= wx.CB_READONLY, choices=app_state.current_speaker.list_voice_options())
		self.cb_model_options.Bind(wx.EVT_COMBOBOX, self.change_voice_params)

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
		szr_voice_params.Add(self.cb_tts_engines, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.cb_model_options, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.cb_speaker_voices, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		szr_voice_params.Add(self.txt_sample_synth, 0, wx.ALL|wx.EXPAND, 5)
		szr_voice_params.Add(self.btn_sample, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
		szr_voice_params.Add(self.btn_update_voice, 0, wx.ALL|wx.ALIGN_LEFT, 5)


	def sample(self, event):
		utils.sampleVoice(self.txt_sample_synth.Value)

	def update_voice(self, event):
		app_state.sample_speaker.name = self.txt_voice_name.Value
		app_state.speakers[app_state.speakers.index(app_state.current_speaker)] = app_state.sample_speaker
		app_state.current_speaker = app_state.sample_speaker
		self.parent.update_voices_list()

	def show_multispeaker(self):
		if app_state.sample_speaker.voice_type == Voice.VoiceType.COQUI and app_state.sample_speaker.is_multispeaker:
			self.cb_speaker_voices.Show()
			self.cb_speaker_voices.Set(app_state.sample_speaker.list_speakers())
			if app_state.sample_speaker.speaker:
				self.cb_speaker_voices.SetValue(app_state.sample_speaker.speaker)
		else:
			self.cb_speaker_voices.Hide()
		self.Layout()

	def update_voice_fields(self, event):
		self.txt_voice_name.Value = app_state.sample_speaker.name
		self.cb_tts_engines.Select(list(Voice.VoiceType.__members__.values()).index(app_state.sample_speaker.voice_type))
		self.cb_model_options.Set(app_state.sample_speaker.list_voice_options())
		try:
			self.cb_model_options.Select(app_state.sample_speaker.list_voice_options().index(app_state.sample_speaker.voice_option))
		except:
			self.cb_model_options.Select(0)
		self.show_multispeaker()

	def change_tts_engine(self, event):
		app_state.sample_speaker = Voice(list(Voice.VoiceType.__members__.values())[self.cb_tts_engines.GetSelection()])
		self.update_voice_fields(event)

	def change_voice_params(self, event):
		self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
		self.Layout()
		option_name = self.cb_model_options.GetStringSelection()
		if app_state.sample_speaker.voice_type == Voice.VoiceType.COQUI:
			if not app_state.sample_speaker.is_model_downloaded(option_name):
				message_download = wx.MessageDialog(
					None,
					f"You do not have\n{option_name}\n downloaded. Would you like to download it? It could take a long time and lots of storage",
					"Downlaod this model?",
					wx.CANCEL
				).ShowModal()
				if(message_download != wx.ID_OK):
					return
		
		app_state.sample_speaker.set_voice_params(voice=option_name)

		if app_state.sample_speaker.voice_type == Voice.VoiceType.COQUI and app_state.sample_speaker.is_multispeaker:
			app_state.sample_speaker.set_voice_params(speaker=self.cb_speaker_voices.GetStringSelection())

		self.show_multispeaker()
		self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

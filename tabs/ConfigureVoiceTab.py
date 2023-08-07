import synth
from pydub.playback import play
from pydub import AudioSegment
import wx
from Voice import Voice

class ConfigureVoiceTab(wx.Panel):
	def __init__(self, notebook, parent):
		super().__init__(notebook)
		self.parent = parent
		# EDIT VOICE PARAMS
		lbl_voice_name = wx.StaticText(self, label="Name")
		self.txt_voice_name = wx.TextCtrl(self, value=synth.currentSpeaker.name)
		self.cb_voice_types = wx.ComboBox(self, style= wx.CB_READONLY, choices=[str(val) for val in Voice.VoiceType])
		self.cb_voice_types.Bind(wx.EVT_COMBOBOX, self.change_voice_type)
		self.cb_voice_options = wx.ComboBox(self, style= wx.CB_READONLY, choices=synth.currentSpeaker.list_voice_options())
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
		synth.sampleSpeaker.speak(self.txt_sample_synth.Value, output)
		play(AudioSegment.from_file(output))

	def update_voice(self, event):
		synth.sampleSpeaker.name = self.txt_voice_name.Value
		synth.speakers[synth.speakers.index(synth.currentSpeaker)] = synth.sampleSpeaker
		synth.currentSpeaker = synth.sampleSpeaker
		self.parent.update_voices_list()

	def show_multispeaker(self):
		if synth.sampleSpeaker.voice_type == Voice.VoiceType.COQUI and synth.sampleSpeaker.is_multispeaker:
			self.cb_speaker_voices.Show()
			self.cb_speaker_voices.Set(synth.sampleSpeaker.list_speakers())
			if synth.sampleSpeaker.speaker:
				self.cb_speaker_voices.SetValue(synth.sampleSpeaker.speaker)
		else:
			self.cb_speaker_voices.Hide()
		self.Layout()

	def update_voice_fields(self, event):
		self.txt_voice_name.Value = synth.sampleSpeaker.name
		self.cb_voice_types.Select(list(Voice.VoiceType.__members__.values()).index(synth.sampleSpeaker.voice_type))
		self.cb_voice_options.Set(synth.sampleSpeaker.list_voice_options())
		self.cb_voice_options.Select(synth.sampleSpeaker.list_voice_options().index(synth.sampleSpeaker.voice_option))
		self.show_multispeaker()

	def change_voice_type(self, event):
		synth.sampleSpeaker = Voice(list(Voice.VoiceType.__members__.values())[self.cb_voice_types.GetSelection()])
		self.update_voice_fields(event)

	def change_voice_params(self, event):
		self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
		self.Layout()
		option_name = self.cb_voice_options.GetStringSelection()
		if synth.sampleSpeaker.voice_type == Voice.VoiceType.COQUI:
			if not synth.sampleSpeaker.is_model_downloaded(option_name):
				message_download = wx.MessageDialog(
					None,
					f"You do not have\n{option_name}\n downloaded. Would you like to download it? It could take a long time and lots of storage",
					"Downlaod this model?",
					wx.CANCEL
				).ShowModal()
				if(message_download != wx.ID_OK):
					return
		
		synth.sampleSpeaker.set_voice_params(voice=option_name)

		if synth.sampleSpeaker.voice_type == Voice.VoiceType.COQUI and synth.sampleSpeaker.is_multispeaker:
			synth.sampleSpeaker.set_voice_params(speaker=self.cb_speaker_voices.GetStringSelection())
		else:
			synth.sampleSpeaker.set_voice_params(speaker=None)
		self.show_multispeaker()
		self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))

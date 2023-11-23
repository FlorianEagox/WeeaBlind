import threading
import app_state
import wx
from Voice import Voice
import utils

class ConfigureVoiceTab(wx.Panel):
	def __init__(self, notebook, parent):
		super().__init__(notebook)
		self.parent = parent

		# Create a grid sizer with extra padding
		grid_sizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=10)

		# Add controls with labels
		lbl_voice_name = wx.StaticText(self, label="Name")
		self.txt_voice_name = wx.TextCtrl(self, value=app_state.current_speaker.name)
		self.add_control_with_label(grid_sizer, lbl_voice_name, self.txt_voice_name)

		lbl_tts_engines = wx.StaticText(self, label="TTS Engine")
		self.cb_tts_engines = wx.Choice(self, choices=[str(val) for val in Voice.VoiceType])
		self.cb_tts_engines.Bind(wx.EVT_CHOICE, self.change_tts_engine)
		self.add_control_with_label(grid_sizer, lbl_tts_engines, self.cb_tts_engines)

		# This is for filtering coqui models by language
		self.lbl_coqui_lang = wx.StaticText(self, label="Language")
		self.cb_coqui_lang = wx.Choice(self, choices=[])
		self.cb_coqui_lang.Bind(wx.EVT_CHOICE, self.change_model_language)
		self.lbl_coqui_lang.Hide()
		self.cb_coqui_lang.Hide()  # Hide by default, show only when multi-speaker Coqui model is selected
		self.add_control_with_label(grid_sizer, self.lbl_coqui_lang, self.cb_coqui_lang)

		lbl_model_options = wx.StaticText(self, label="Model Options")
		self.cb_model_options = wx.Choice(self, choices=app_state.current_speaker.list_voice_options())
		self.cb_model_options.Bind(wx.EVT_CHOICE, self.change_voice_params)
		self.add_control_with_label(grid_sizer, lbl_model_options, self.cb_model_options)
		

		# This is for multispeaker coqui models. Should be hidden by default & shown when model is multispeaker
		self.lbl_speaker_voices = wx.StaticText(self, label="Speaker Voices")
		self.cb_speaker_voices = wx.Choice(self, choices=[])
		self.cb_speaker_voices.Bind(wx.EVT_CHOICE, self.change_voice_params)
		self.lbl_speaker_voices.Hide()
		self.cb_speaker_voices.Hide()  # Hide by default, show only when multi-speaker Coqui model is selected
		self.add_control_with_label(grid_sizer, self.lbl_speaker_voices, self.cb_speaker_voices)

		lbl_sample_text = wx.StaticText(self, label="Sample Text")
		self.txt_sample_text = wx.TextCtrl(self, value="I do be slurpin' that cheese without my momma's permission")
		self.add_control_with_label(grid_sizer, lbl_sample_text, self.txt_sample_text)

		self.btn_sample = wx.Button(self, label="▶️ Sample Voice")
		self.btn_sample.Bind(wx.EVT_BUTTON, self.sample)

		self.btn_update_voice = wx.Button(self, label="Update Voice")
		self.btn_update_voice.Bind(wx.EVT_BUTTON, self.update_voice)

		# Add the buttons to the grid without labels
		grid_sizer.AddStretchSpacer()
		grid_sizer.Add(self.btn_sample, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
		grid_sizer.Add(self.btn_update_voice, 0, wx.ALL | wx.ALIGN_LEFT, 5)

		# Set the grid sizer as the main sizer for the panel with extra padding
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, 15)
		self.SetSizerAndFit(main_sizer)

	def add_control_with_label(self, sizer, label, control):
		sizer.Add(label, 0, wx.ALL|wx.ALIGN_LEFT, 5)
		sizer.Add(control, 0, wx.ALL|wx.EXPAND, 5)

	def sample(self, event):
		utils.sampleVoice(self.txt_sample_text.Value)

	# When the user clicks update voice, asign one in the array to the specification
	def update_voice(self, event):
		app_state.sample_speaker.name = self.txt_voice_name.Value
		app_state.speakers[app_state.speakers.index(app_state.current_speaker)] = app_state.sample_speaker
		app_state.current_speaker = app_state.sample_speaker
		self.parent.update_voices_list()

	# determines weather to show hidden models based on the state of the selected voice model/engine
	def show_hidden(self):
		if app_state.sample_speaker.voice_type == Voice.VoiceType.COQUI:
				self.lbl_coqui_lang.Show()
				self.cb_coqui_lang.Show()
				self.cb_coqui_lang.Set(list(app_state.sample_speaker.langs))
				self.cb_coqui_lang.Select(app_state.sample_speaker.langs.index(app_state.sample_speaker.selected_lang))
				self.change_model_language(None)
				if app_state.sample_speaker.is_multispeaker:
					self.lbl_speaker_voices.Show()
					self.cb_speaker_voices.Show()
					self.cb_speaker_voices.Set(app_state.sample_speaker.list_speakers())
					if app_state.sample_speaker.speaker:
						self.cb_speaker_voices.SetStringSelection(app_state.sample_speaker.speaker)
				else:
					self.lbl_speaker_voices.Hide()
					self.cb_speaker_voices.Hide()
		else:
			self.lbl_coqui_lang.Hide()
			self.cb_coqui_lang.Hide()

		self.Layout()

	# Populate the form with the current sample speaker's params
	def update_voice_fields(self, event):
		self.txt_voice_name.Value = app_state.sample_speaker.name
		self.cb_tts_engines.Select(list(Voice.VoiceType.__members__.values()).index(app_state.sample_speaker.voice_type))
		self.cb_model_options.Set(app_state.sample_speaker.list_voice_options())
		self.show_hidden()
		try:
			self.cb_model_options.Select(self.cb_model_options.GetStrings().index(app_state.sample_speaker.voice_option))
		except:
			self.cb_model_options.Select(0)

	def change_tts_engine(self, event):
		app_state.sample_speaker = Voice(list(Voice.VoiceType.__members__.values())[self.cb_tts_engines.GetSelection()])
		self.update_voice_fields(event)

	# Update the sample speaker to the specification
	def change_voice_params(self, event):
		self.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
		self.Layout()
		option_name = self.cb_model_options.GetStringSelection()
		
		def run_after():
			if app_state.sample_speaker.is_multispeaker:
				app_state.sample_speaker.set_voice_params(speaker=self.cb_speaker_voices.GetStringSelection())
			self.update_voice_fields(event)
			self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
			dialog_download.Destroy()
		
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
				dialog_download = wx.ProgressDialog("Downloading Model", "starting", 100, self)

				def download_progress(progress, status=None):
					if progress == -1:
						wx.CallAfter(run_after)
					else:
						wx.CallAfter(dialog_download.Update, progress, f"{progress}% - {status} \n {option_name}")
				threading.Thread(target=app_state.sample_speaker.set_voice_params, kwargs={"voice": option_name, "progress": download_progress}).start()
		else:
			app_state.sample_speaker.set_voice_params(voice=option_name)
			run_after()

	def change_model_language(self, event):
		if self.cb_coqui_lang.GetSelection() == 0: # If they have "All Voices" selected, don't filter
			self.cb_model_options.Set(app_state.sample_speaker.list_voice_options())
		else:
			self.cb_model_options.Set([model for model in app_state.sample_speaker.list_voice_options() if f"/{self.cb_coqui_lang.GetStringSelection()}/" in model])
			app_state.sample_speaker.selected_lang = self.cb_coqui_lang.GetStringSelection()

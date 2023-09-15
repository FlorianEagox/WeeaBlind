import wx
import app_state
import ffmpeg

class ListStreamsTab(wx.Panel):
	def __init__(self, parent, context):
		super().__init__(parent)
		
		self.context = context

		self.rb_audio = wx.RadioBox(self, majorDimension=1)
		self.rb_subs = wx.RadioBox(self, majorDimension=1)

		# Create a sizer for layout
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(self, label="Select an Audio Stream:"), 0, wx.ALL, 5)
		sizer.Add(self.rb_audio, 0, wx.ALL | wx.EXPAND, 5)
		sizer.Add(wx.StaticText(self, label="Select a Subtitle Stream:"), 0, wx.ALL, 5)
		sizer.Add(self.rb_subs, 0, wx.ALL | wx.EXPAND, 5)

		self.SetSizer(sizer)

	def populate_streams(self, streams):
		# This code is some of the worst code, i hate it so much, but WX DOESN'T LET ME RESET THE CHOICES LIKE WITH **EVERY** OTHER LIST COMPONENT
		_rb_audio = self.rb_audio
		self.rb_audio = wx.RadioBox(self,
			choices=[f"Stream #{stream['index']} ({stream['tags'].get('language', 'unknown')})" for stream in streams["audio"]],
			style=wx.RA_SPECIFY_COLS
		)
		self.rb_audio.Bind(wx.EVT_RADIOBOX, lambda: self.on_audio_selection(None, streams))
		self.GetSizer().Replace(_rb_audio, lambda: self.rb_audio(None, streams))
		_rb_audio.Destroy()
		
		_rb_subs_copy = self.rb_subs
		self.rb_subs = wx.RadioBox(self,
			choices=[f"Stream #{stream['index']} ({stream['tags'].get('language', 'unknown')})" for stream in streams["subs"]],
			style=wx.RA_SPECIFY_COLS
		)
		self.rb_subs.Bind(wx.EVT_RADIOBOX, self.on_subtitle_selection)
		self.GetSizer().Replace(_rb_subs_copy, self.rb_subs)
		_rb_subs_copy.Destroy()

		self.Layout()

	def on_audio_selection(self, event):
		selected_audio = self.rb_audio.GetStringSelection()
		

	def on_subtitle_selection(self, event, streams):
		app_state.video.change_subs(streams['subs'][self.rb_audio.GetSelection()])
		self.context.tab_subtitles.create_entries()
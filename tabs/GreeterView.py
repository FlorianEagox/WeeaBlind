import wx
import feature_support

class GreeterView(wx.Panel):
	def __init__(self, parent, context):
		super().__init__(parent)

		self.scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.scroll_panel.SetSizer(vbox)
		self.scroll_panel.SetScrollRate(0, 20)
  
		title = wx.StaticText(self.scroll_panel, label="Welcome to Weeablind")
		title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		title.SetFont(title_font)
		vbox.Add(title, 0, wx.ALIGN_LEFT | wx.TOP | wx.LEFT, 20)

		img = wx.Image("logo.png", wx.BITMAP_TYPE_ANY)
		img.Rescale(200, 200)
		bmp = wx.StaticBitmap(self.scroll_panel, wx.ID_ANY, wx.Bitmap(img))
		vbox.Add(bmp, 0, wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT, 20)

		# Add introduction text
		intro_text = "Welcome to WeeaBlind, your companion for dubbing multi-lingual media using modern AI technologies. This tool bridges the gap for individuals with visual impairments, dyslexia, learning disabilities,  or anyone who prefers listening over reading subtitles. Dive into your favorite shows and videos with ease,   thanks to our blend of speech synthesis, diarization, language identification, and voice cloning technologies."
		introduction = wx.StaticText(self.scroll_panel, label=intro_text)
		introduction.Wrap(400)  # Wrap text to a maximum width of 400 pixels
		vbox.Add(introduction, 0, wx.ALIGN_LEFT | wx.TOP | wx.LEFT, 20)

		# Add a section about how to use the application
		usage_section = wx.StaticText(self.scroll_panel, label="How to Use Weeablind:")
		usage_section_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		usage_section.SetFont(usage_section_font)
		vbox.Add(usage_section, 0, wx.ALIGN_LEFT | wx.TOP | wx.LEFT, 20)

		# Add usage instructions
		usage_guide = """
Start by importing a video file or pasting a YouTube Link
Make sure the correct audio and subtitle track are selected in the List Streams tab
Next, configure the TTS voice you'd like to dub the video with
--------------------
For Advanced Use
If the video contains multiple spoken languages, use the language identification and filter features
If you want to remove spoken vocals in the video's source language, use the remove "vocals button"

"""
		usage_text = wx.StaticText(self.scroll_panel, label=usage_guide)
		usage_text.Wrap(400)
		vbox.Add(usage_text, 0, wx.ALIGN_LEFT | wx.TOP | wx.LEFT, 20)

		# Add a section about the currently supported features
		feature_section = wx.StaticText(self.scroll_panel, label="Currently Supported Features:")
		feature_section_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		feature_section.SetFont(feature_section_font)
		vbox.Add(feature_section, 0, wx.ALIGN_LEFT | wx.TOP | wx.LEFT, 20)

		# Populate feature support information based on feature_support.py
		feature_list = [
			"FFmpeg Supported" if feature_support.ffmpeg_supported else "FFmpeg Not Supported",
			"Diarization Supported" if feature_support.diarization_supported else "Diarization Not Supported",
			"OCR Supported" if feature_support.ocr_supported else "OCR Not Supported",
			"Vocal Isolation Supported" if feature_support.vocal_isolation_supported else "Vocal Isolation Not Supported",
			"Downloads Supported" if feature_support.downloads_supported else "Downloads Not Supported",
			"Espeak Supported" if feature_support.espeak_supported else "Espeak Not Supported",
			"Coqui Supported" if feature_support.coqui_supported else "Coqui Not Supported",
			"GPU Supported" if feature_support.gpu_supported else "GPU Not Supported"
		]

		for feature in feature_list:
			feature_text = wx.StaticText(self.scroll_panel, label=feature)
			vbox.Add(feature_text, 0, wx.ALIGN_LEFT | wx.TOP | wx.LEFT, 20)

		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, border=10)
		self.SetSizerAndFit(main_sizer)


	def add_supported_features(self):
		self.rich_text.Newline()
		self.rich_text.BeginFontSize(10)
		self.rich_text.BeginBold()
		self.rich_text.WriteText("Supported Features at Runtime:")
		self.rich_text.EndBold()
		self.rich_text.Newline()
		
		# Dynamically check and display supported features
		features = {
			"FFmpeg": feature_support.ffmpeg_supported,
			"Diarization": feature_support.diarization_supported,
			"OCR": feature_support.ocr_supported,
			"Language Detection": feature_support.language_detection_supported,
			"Vocal Isolation": feature_support.vocal_isolation_supported,
			"YouTube Downloads": feature_support.downloads_supported,
			"Espeak": feature_support.espeak_supported,
			"Coqui TTS": feature_support.coqui_supported,
			"PyTorch": feature_support.torch_supported,
			"GPU Support": feature_support.gpu_supported,
		}
		
		for feature, supported in features.items():
			self.rich_text.BeginTextColour(wx.Colour(0, 128, 0) if supported else wx.Colour(128, 0, 0))
			self.rich_text.WriteText(f"{feature}: {'Supported' if supported else 'Not Supported'}")
			self.rich_text.Newline()
			self.rich_text.EndTextColour()

		self.rich_text.EndFontSize()

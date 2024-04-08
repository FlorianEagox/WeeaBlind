import wx
import wx.html
import markdown

class GreeterView(wx.Panel):
	def __init__(self, parent, context):
		super().__init__(parent)
		self.html_display = wx.html.HtmlWindow(self, style=wx.TAB_TRAVERSAL)

		# md_text = "<h1>Sup Faggots!</h1>"
		with open("README.md", 'r') as file:
			base_md = markdown.markdown(file.read()) #  markdown.markdown(file)
		
		self.html_display.SetPage(base_md)
		print(self.html_display.IsFocusable(``))

		sizer = wx.BoxSizer()
		sizer.Add(self.html_display, 1, wx.EXPAND, 5)
		self.SetSizerAndFit(sizer)

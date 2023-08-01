import wx

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


panel = wx.Panel(frame)
btn_choose_file = wx.Button(panel, label="Choose FIle")
btn_choose_file.Bind(wx.EVT_BUTTON, open_file)

txt_main_file = wx.TextCtrl(panel, wx.TC_LEFT, "saiki.mkv")
lbl_title = wx.StaticText(panel, label="WeeaBlind")
sizer = wx.BoxSizer(wx.VERTICAL)
sizer.Add(lbl_title, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(btn_choose_file, 0, wx.ALL|wx.CENTER, 5)
sizer.Add(txt_main_file, 0, wx.ALL|wx.CENTER, 5)
panel.SetSizer(sizer)

frame.Show()
app.MainLoop()

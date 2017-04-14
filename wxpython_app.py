import wx

class ImagePanel(wx.Panel):
    def __init__(self, parent):
        super(ImagePanel, self).__init__(parent)
        # Load the image data into a Bitmap
        theBitmap = wx.Bitmap("images/house1_small_corner.jpg")
        # Create a control that can display the
        # bitmap on the screen.
        self.bitmap = wx.StaticBitmap(self, bitmap=theBitmap)

class MyFrame(wx.Frame):
    def __init__(self, parent, title=""):
        super(MyFrame, self).__init__(parent, title=title)
        # Set an application icon
        # self.SetIcon(wx.Icon("appIcon.png"))
        # Set the panel
        self.panel = ImagePanel(self)

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="Main Frame")
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
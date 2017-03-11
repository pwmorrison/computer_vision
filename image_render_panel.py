import wx

"""
Panel for rendering an image.
"""

class ImageRenderPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.image = None

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        if self.image is not None:
            dc.DrawBitmap(self.image, 0, 0)
        else:
            dc.SetPen(wx.Pen("red"))
            dc.SetBrush(wx.Brush("red"))
            dc.DrawRectangle(220 + 10,10,200 + 10,200)

    def set_image(self, image):
        self.image = image

if __name__ == '__main__':
    app = wx.App()
    frame = wx.Frame(None)
    panel = ImageRenderPanel(frame)
    frame.Show()
    app.MainLoop()

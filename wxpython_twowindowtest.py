import wx


class Controller():
    def __init__(self):
        app = wx.App(False)
        frame1 = wx.Frame(None, -1, "Frame 1", size = (500, 500))
        frame2 = wx.Frame(None, -1, "Frame 2", size = (500, 500))
        self.panel1 = MyPanel(frame1, -1)
        self.panel2 = MyPanel(frame2, -1)
        frame1.Show(True)
        frame2.Show(True)

        self.timer = wx.Timer()
        app.Bind(wx.EVT_TIMER, self.processing_loop, self.timer)
        self.timer.Start(2000)

        # Must do this last; any following setup code isn't executed.
        app.MainLoop()


    def processing_loop(self, event):
        print(event)
        self.panel1.Refresh()

class MyPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)
        print("Painting panel.")


def test():
    controller = Controller()

if __name__ == "__main__":
    test()

import wx

class MyPanel(wx.Panel):
    """"""

    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent)

    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        #blue non-filled rectangle
        dc.SetPen(wx.Pen("blue"))
        dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
        dc.DrawRectangle(10,10,200,200)

        #red filled rectangle
        dc.SetPen(wx.Pen("red"))
        dc.SetBrush(wx.Brush("red"))
        dc.DrawRectangle(220,10,200,200)

class MyFrame(wx.Frame):
    """"""

    def __init__(self):
        """"""
        wx.Frame.__init__(self, None, title="Test Maximize")
        panel = MyPanel(self)
        self.Show()
        self.Maximize(True)

def test_1():
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()

class MyPanel2(wx.Panel):
    """ class MyPanel creates a panel to draw on, inherits wx.Panel """
    def __init__(self, parent, id):
        # create a panel
        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    # def OnPaint(self, evt):
    #     """set up the device context (DC) for painting"""
    #     self.dc = wx.PaintDC(self)
    #     self.dc.BeginDrawing()
    #     self.dc.SetPen(wx.Pen("red",style=wx.TRANSPARENT))
    #     self.dc.SetBrush(wx.Brush("red", wx.SOLID))
    #     # set x, y, w, h for rectangle
    #     self.dc.DrawRectangle(250,250,50, 50)
    #     self.dc.EndDrawing()
    #     del self.dc
    def OnPaint(self, event):
        """set up the device context (DC) for painting"""
        dc = wx.PaintDC(self)

        #blue non-filled rectangle
        dc.SetPen(wx.Pen("blue"))
        dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
        dc.DrawRectangle(10,10,200,200)

        #red filled rectangle
        dc.SetPen(wx.Pen("red"))
        dc.SetBrush(wx.Brush("red"))
        dc.DrawRectangle(220,10,200,200)



def test_2():
    # app = wx.PySimpleApp()
    app = wx.App(False)
    # create a window/frame, no parent, -1 is default ID
    frame = wx.Frame(None, -1, "Drawing A Rectangle...", size = (500, 500), style=wx.NO_BORDER)
    frame.Maximize(True)
    # call the derived class, -1 is default ID
    MyPanel2(frame, -1)
    # show the frame
    frame.Show(True)
    # start the event loop
    app.MainLoop()

if __name__ == "__main__":
    # test_1()
    test_2()

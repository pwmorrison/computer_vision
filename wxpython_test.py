import wx

myEVT_CUSTOM = wx.NewEventType()
EVT_CUSTOM = wx.PyEventBinder(myEVT_CUSTOM, 1)
class MyEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        myVal = None
        # print(myV)

    def SetMyVal(self, val):
        self.myVal = val

    def GetMyVal(self):
        return self.myVal

class MyPanel(wx.Panel):
    """ class MyPanel creates a panel to draw on, inherits wx.Panel """
    def __init__(self, parent, id):
        # create a panel
        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("white")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

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

        for i in range(10):
            #red filled rectangle
            dc.SetPen(wx.Pen("red"))
            dc.SetBrush(wx.Brush("red"))
            dc.DrawRectangle(220 + i*10,10,200 + i*10,200)

        print("Painting.")

        event = MyEvent(myEVT_CUSTOM, self.GetId())
        event.SetMyVal('here is some custom data')
        self.Bind(EVT_CUSTOM, self.render_another_square)
        self.GetEventHandler().ProcessEvent(event)

    def render_another_square(self, event):
        """set up the device context (DC) for painting"""
        print(event)
        dc = wx.PaintDC(self)
        #blue non-filled rectangle
        dc.SetPen(wx.Pen("blue"))
        dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
        dc.DrawRectangle(10,210,200,200)

def test():
    app = wx.App(False)

    full_screen = False

    # create a window/frame, no parent, -1 is default ID
    if not full_screen:
        frame = wx.Frame(None, -1, "Drawing A Rectangle...", size = (500, 500))
    else:
        frame = wx.Frame(None, -1, "Drawing A Rectangle...", size = (500, 500), style=wx.NO_BORDER)
        frame.Maximize(True)

    # Add a panel to the frame, -1 is default ID
    MyPanel(frame, -1)
    # Show the frame
    frame.Show(True)
    # Start the event loop
    app.MainLoop()

if __name__ == "__main__":
    test()

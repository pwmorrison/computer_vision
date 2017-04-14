import wx

class GrayCodePanel(wx.Panel):
    """
    Panel to render Gray code patterns.
    """
    def __init__(self, parent, id, window_size):
        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("black")

        self.window_size = window_size
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        # print("OnPaint")
        dc = wx.PaintDC(self)

        # Render static stuff, that persists between re-paints.
        if 1:
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

def main():
    app = wx.App(False)

    window_size = (500, 500)
    frame = wx.Frame(None, -1, "Gray code projection", size=window_size)

    # Add a panel to the frame, -1 is default ID
    gray_code_panel = GrayCodePanel(frame, -1, window_size)
    # Show the frame
    frame.Show(True)

    # Start the event loop
    app.MainLoop()

if __name__ == '__main__':
    main()
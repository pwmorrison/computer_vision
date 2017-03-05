import wx
from gray_code import generate_gray_code_sequence, generate_gray_code_bit_planes

"""
Main file for rendering gray code patterns, and capturing images of the patterns.

How this should work:

1. It should all be within a wxPython app, since that needs its own event loop.
This will also allow us to capture key presses, for controlling the projection, etc.

2. We need to implement a state machine, for alternating between projection, capture, etc. We can probably do this by
having a custom Event class, that stores the current state, and the state progression sequence. The Panel should
invoke all the rendering calls, with assistance from the gray code class for getting the bit sequences.

The Panel onpaint method should paint according to the current state. It should also be the only function



"""

class GrayCodeState():
    """
    Class representing the sequence of gray code projections.
    This class supplies the bit planes that are rendered, and keeps track of the sequence of rendered bit planes.
    """
    def __init__(self):
        width = 12
        height = 8
        # Generate the gray code sequences to cover the largest possible coordinate.
        gray_code_arrays = generate_gray_code_sequence(max(width, height))

        # Convert the sequence to bit planes.
        self.bit_planes = generate_gray_code_bit_planes(gray_code_arrays)

        self.current_bit_plane = 0
        self.final_bit_plane = self.bit_planes.shape[0]
        self.sequence_finished = False

    def progress_state(self):
        """
        Progress the current state to the next state.
        """
        self.current_bit_plane += 1
        if self.current_bit_plane > self.final_bit_plane:
            self.current_bit_plane = self.final_bit_plane
            self.sequence_finished = True

    def is_sequence_finished(self):
        return self.sequence_finished

    def get_current_bit_plane(self):
        """
        Gets the bit plane for the current state.
        """
        # TODO For now, just return the current bit plane number.
        return self.current_bit_plane

myEVT_GRAY_CODE = wx.NewEventType()
EVT_GRAY_CODE = wx.PyEventBinder(myEVT_GRAY_CODE, 1)
class GrayCodeEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id, gray_code_state):
        wx.PyCommandEvent.__init__(self, evtType, id)
        myVal = None
        self.gray_code_state = gray_code_state
        # print(myV)

    def SetMyVal(self, val):
        self.myVal = val

    def GetMyVal(self):
        return self.myVal

class GrayCodePanel(wx.Panel):
    """
    Panel to render Gray code patterns.
    """
    def __init__(self, parent, id, window_size):
        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("black")
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        print("OnPaint")
        dc = wx.PaintDC(self)

        if 0:
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

        gray_code_state = GrayCodeState()

        event = GrayCodeEvent(myEVT_GRAY_CODE, self.GetId(), gray_code_state)
        event.SetMyVal('here is some custom data')
        self.Bind(EVT_GRAY_CODE, self.render_gray_code)
        self.GetEventHandler().ProcessEvent(event)

    def render_gray_code(self, event):
        """
        event -- The event that triggered this rendering. Contains the state of the Gray code sequence.
        TODO: To include camera capture, we'll need to have some kind of switch in this function. If the next event is
        not a render, capture an image, or something.
        """
        print("render_gray_code")
        state = event.gray_code_state

        # Get the current bit plane.
        bit_plane = state.get_current_bit_plane()

        # Render the current bit plane.
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen("blue"))
        dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
        dc.DrawRectangle(10 + bit_plane * 20, 210, 200, 200)

        # Increment the gray code state.
        state.progress_state()

        if not state.is_sequence_finished():
            # Trigger the event again, so that we move onto the next state.
            event = GrayCodeEvent(myEVT_GRAY_CODE, self.GetId(), state)
            self.GetEventHandler().ProcessEvent(event)

def main(full_screen):
    app = wx.App(False)
    # Create frame, no parent, -1 is default ID.
    if not full_screen:
        window_size = (500, 500)
        frame = wx.Frame(None, -1, "Gray code capture", size=window_size)
    else:
        window_size = wx.GetDisplaySize()
        frame = wx.Frame(None, -1, "Gray code capture", size=window_size, style=wx.NO_BORDER)
        frame.Maximize(True)
    # Add a panel to the frame, -1 is default ID
    GrayCodePanel(frame, -1, window_size)
    # Show the frame
    frame.Show(True)
    # Start the event loop
    app.MainLoop()

if __name__ == '__main__':
    full_screen = False
    main(full_screen)

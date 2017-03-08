import wx
import time
import numpy as np
import cv2
from gray_code import generate_gray_code_sequence, generate_gray_code_bit_planes
from gray_code_camera_panel import GrayCodeCameraPanel

"""
Main file for rendering gray code patterns, and capturing images of the patterns.
"""

class GrayCodeState():
    """
    Class representing the sequence of gray code projections.
    This class supplies the bit planes that are rendered, and keeps track of the sequence of rendered bit planes.
    """
    def __init__(self, window_size):
        width = window_size[0]
        height = window_size[1]
        # Generate the gray code sequences to cover the largest possible coordinate.
        gray_code_arrays = generate_gray_code_sequence(max(width, height))

        # Convert the sequence to bit planes.
        self.bit_planes = generate_gray_code_bit_planes(gray_code_arrays)

        self.current_bit_plane = 0
        self.final_bit_plane = self.bit_planes.shape[0] - 1
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
        bit_plane_index = len(self.bit_planes) - self.current_bit_plane - 1
        print("Getting bit plane for index:", bit_plane_index)
        return self.bit_planes[bit_plane_index]
        # return self.bit_planes[self.current_bit_plane]


class GrayCodePanel(wx.Panel):
    """
    Panel to render Gray code patterns.
    """
    def __init__(self, parent, id, window_size):
        wx.Panel.__init__(self, parent, id)
        self.SetBackgroundColour("black")

        self.window_size = window_size

        self.gray_code_state = GrayCodeState(window_size)

        # Create a timer that triggers a refresh, to paint a new Gray code bit plane.
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.timer_update, self.timer)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # Start the timer, to trigger the first state change at some future time.
        self.start_timer()

    def OnPaint(self, event):
        print("OnPaint")
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

        # Render dynamic Gray code stuff.
        if 1:
            state = self.gray_code_state
            self.render_gray_code2(state)
            if 0:
                # Increment the gray code state.
                state.progress_state()
                if not state.is_sequence_finished():
                    # Start a new timer, to render the next bit plane.
                    self.timer.Start(2000)

    def timer_update(self, event):
        """
        Timer event handler.
        Basically just triggers a re-paint when the timer is triggered.
        Also sets the next timer event, if the pattern isn't finished.
        """
        self.timer.Stop()
        self.Refresh()

        state = self.gray_code_state
        state.progress_state()
        self.start_timer()

    def start_timer(self):
        state = self.gray_code_state
        if not state.is_sequence_finished():
            # Start a new timer, to render the next bit plane.
            print("Starting timer.")
            self.timer.Start(2000)

    def render_gray_code2(self, state):
        """
        event -- The event that triggered this rendering. Contains the state of the Gray code sequence.
        TODO: To include camera capture, we'll need to have some kind of switch in this function. If the next event is
        not a render, capture an image, or something.
        """
        print("render_gray_code")
        # state = event.gray_code_state

        # Get the current bit plane.
        bit_plane = state.get_current_bit_plane()
        print(bit_plane)

        # Render the current bit plane.
        dc = wx.PaintDC(self)

        if 0:
            dc.SetPen(wx.Pen("blue"))
            dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT)) #set brush transparent for non-filled rectangle
            dc.DrawRectangle(10 + bit_plane * 20, 310, 200, 200)

        dc.SetPen(wx.Pen("white"))
        dc.SetBrush(wx.Brush("white"))
        # dc.DrawRectangle(10 + bit_plane * 20, 310, 200, 200)
        for x, bit_val in enumerate(bit_plane):
            if bit_val == 1:
                dc.DrawRectangle(x, 0, 1, self.window_size[1])

def main(full_screen, capture_images):

    app = wx.App(False)
    # Create frame, no parent, -1 is default ID.
    if not full_screen:
        window_size = (500, 500)
        frame = wx.Frame(None, -1, "Gray code projection", size=window_size)
    else:
        window_size = wx.GetDisplaySize()
        frame = wx.Frame(None, -1, "Gray code projection", size=window_size, style=wx.NO_BORDER)
        frame.Maximize(True)
    # Add a panel to the frame, -1 is default ID
    GrayCodePanel(frame, -1, window_size)
    # Show the frame
    frame.Show(True)

    if capture_images:
        # Set up the camera.
        camera_number = 0
        capture = cv2.VideoCapture(camera_number)
        camera_frame = wx.Frame(None, -1, "Camera capture", size=window_size)
        cap = GrayCodeCameraPanel(camera_frame, capture)
        camera_frame.Show(True)


    # Start the event loop
    app.MainLoop()

if __name__ == '__main__':
    full_screen = False
    capture_images = True
    main(full_screen, capture_images)

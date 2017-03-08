import wx
import cv2

"""
Code taken from here: http://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
Good tutorial: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video
Property IDs: http://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get
"""

class GrayCodeCameraPanel(wx.Panel):
    def __init__(self, parent, capture, fps=15):
        wx.Panel.__init__(self, parent)

        self.capture = capture
        ret, frame = self.capture.read()

        height, width = frame.shape[:2]
        parent.SetSize((width, height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.bmp = wx.BitmapFromBuffer(width, height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()

if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    print(capture)
    # capture.set(cv2.CV_CAP_PROP_FRAME_WIDTH, 320)
    # capture.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, 240)

    app = wx.App()
    frame = wx.Frame(None)
    cap = GrayCodeCameraPanel(frame, capture)
    frame.Show()
    app.MainLoop()

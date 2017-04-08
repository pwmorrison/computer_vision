import wx
import cv2
import pygame
import pygame.camera
from PIL import Image

"""
Code taken from here: http://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
Good tutorial: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video
Property IDs: http://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get

On Linux, instead of using pygame, which is slow and flaky, we can make an external call to streamer:
streamer -f ppm -s 640x480 -o image.ppm
"""

class GrayCodeCameraPanel(wx.Panel):
    def __init__(self, parent, capture, capture_library, fps=15):
        wx.Panel.__init__(self, parent)

        self.capture = capture
        self.capture_library = capture_library
        # ret, frame = self.capture.read()

        # buffer_size = self.capture.get(cv2.CAP_PROP_BUFFERSIZE)
        # print("OpenCV buffer size: %d" % (buffer_size))

        # Get a frame.
        if capture_library == "opencv":
            frame, width, height = self.capture_frame_opencv()
        elif capture_library == "pygame":
            frame, width, height = self.capture_frame_pygame()
        self.bmp = wx.BitmapFromBuffer(width, height, frame)

        # height, width = frame.shape[:2]
        # parent.SetSize((width, height))
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #
        # self.bmp = wx.BitmapFromBuffer(width, height, frame)

        if 0:
            self.timer = wx.Timer(self)
            self.timer.Start(1000./fps)
            self.Bind(wx.EVT_TIMER, self.NextFrame)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.image_number = 0

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        # dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)
        print("Painting image %d" % self.image_number)

    # def capture_image(self):
    #     # Read a coupld of frames to get through the buffer to the current image.
    #     ret, frame = self.capture.read()
    #     ret, frame = self.capture.read()
    #     if ret:
    #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         self.bmp.CopyFromBuffer(frame)
    #         self.image_number += 1
    #         print("Capturing image %d" % self.image_number)
    #         self.Refresh()
    #     return frame

    def capture_frame_opencv(self):
        ret, frame = self.capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        print(width, height)
        return frame, width, height


    def capture_frame_pygame(self):
        image = self.capture.get_image()
        # pygame.image.save(image, 'pygame_image.jpeg')
        width, height = image.get_size()
        pil_string_image = pygame.image.tostring(image, "RGB", False)

        return pil_string_image, width, height

    def capture_image(self):
        # Get a frame.
        if self.capture_library == "opencv":
            frame, width, height = self.capture_frame_opencv()
        elif self.capture_library == "pygame":
            frame, width, height = self.capture_frame_pygame()

        self.bmp.CopyFromBuffer(frame)

        print("Capturing image %d" % self.image_number)
        self.Refresh()

        im = Image.frombytes("RGB", (640, 480), frame)
        return im

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

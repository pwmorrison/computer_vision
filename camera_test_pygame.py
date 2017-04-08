import wx
import cv2
import pygame
import pygame.camera

"""
Code taken from here: http://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
Good tutorial: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video
Property IDs: http://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get
"""

capture_library = "pygame"

class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=10):
        wx.Panel.__init__(self, parent)

        self.capture = capture

        self.wx_im = wx.EmptyImage(640, 480)

        # Get a frame.
        if capture_library == "opencv":
            frame, width, height = self.capture_frame_opencv()
        elif capture_library == "pygame":
            frame, width, height = self.capture_frame_pygame()
        self.bmp = wx.BitmapFromBuffer(width, height, frame)

        parent.SetSize((width, height))

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)


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


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        # print("bmp:", self.bmp.GetSize())
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        self.capture_image()
        self.Refresh()

    def capture_image(self):
        # Get a frame.
        if capture_library == "opencv":
            frame, width, height = self.capture_frame_opencv()
        elif capture_library == "pygame":
            frame, width, height = self.capture_frame_pygame()

        self.bmp.CopyFromBuffer(frame)


if __name__ == '__main__':

    if capture_library == "opencv":
        capture = cv2.VideoCapture(0)
    elif capture_library == "pygame":
        pygame.init()
        pygame.camera.init()
        print(pygame.camera.list_cameras())
        cam = pygame.camera.Camera("/dev/video0", (640, 480))
        cam.start()
        # i = 0
        # while i < 1000000:
        #     if cam.query_image():
        #         break
        #     i += 1
        # image = cam.get_image()
        # pygame.image.save(image, 'pygame_image.jpeg')
        # print(image)

        capture = cam

    print("Capture/camera:", capture)

    app = wx.App()
    frame = wx.Frame(None)
    cap = ShowCapture(frame, capture)
    frame.Show()
    app.MainLoop()

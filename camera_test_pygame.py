import wx
import cv2
import sys
# import skvideo.io
import pygame
import pygame.camera
from pygame.locals import *
import numpy as np
from PIL import Image

"""
Code taken from here: http://stackoverflow.com/questions/14804741/opencv-integration-with-wxpython
Good tutorial: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video
Property IDs: http://docs.opencv.org/2.4/modules/highgui/doc/reading_and_writing_images_and_video.html#videocapture-get
"""

capture_library = "opencv"

class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=10):
        wx.Panel.__init__(self, parent)

        self.capture = capture

        self.wx_im = wx.EmptyImage(640, 480)

        # Get a frame.
        if capture_library == "opencv":
            frame, width, height = self.capture_frame_opencv()
            self.bmp = wx.BitmapFromBuffer(width, height, frame)
            parent.SetSize((width, height))
        # elif capture_library == "pygame":
        #     frame, width, height = self.capture_frame_pygame()
        #     self.bmp = frame
        self.capture_image()


        # print("Frame:", frame)
        # print("Frame shape:", frame.shape)
        # self.bmp = wx.BitmapFromBuffer(width, height, frame)

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)

    def capture_frame_opencv(self):
        ret, frame = self.capture.read()
        # Try again.
        # if frame is None:
        #     ret, frame = self.capture.read()
        # print(ret, frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame.shape[:2]
        print(width, height)
        # width, height = cv2.GetSize(frame) # PAUL: Not sure if this is correct. Possibly call shape[:2].
        return frame, width, height


    def capture_frame_pygame(self):
        image = self.capture.get_image()
        # pygame.image.save(image, 'pygame_image.jpeg')
        width, height = image.get_size()
        if 0:
            image = pygame.surfarray.array3d(image)
            image = np.array(image)
            image = image.astype(np.uint8)
        else:
            surf = image
            # data = pygame.image.tostring(surf, "RGB")
            # data = pygame.surfarray.array3d(surf)
            if 1:
                pil_string_image = pygame.image.tostring(surf, "RGB", False)
                # im = Image.frombytes("RGB", (640, 480), pil_string_image)


                # self.wx_im.SetData(im.convert("RGB").tobytes())
                # wx_bitmap = wx.BitmapFromImage(self.wx_im)
                wx_bitmap = wx.BitmapFromBuffer(width, height, pil_string_image)

                # im.save("pil_image.png")
                # data = im.getdata()
                # data = np.array(data)
                # data = np.reshape(data, (640, 480, 3))
            # print(data)
            # print(data.dtype, data.shape)
            # data = np.array(data)
            # print(data)
            # image = wx.ImageFromData(surf.get_width(), surf.get_height(), data).ConvertToBitmap(24)
            # image = wx.BitmapFromBuffer(surf.get_width(), surf.get_height(), data)
        # print(type(image))
        # print(image[0])
        # image = np.transpose(image, [1, 0, 2])
        # print(image.shape)
        # print(image.dtype)
        # print(image, width, height)
        return wx_bitmap, surf.get_width(), surf.get_height()
        # return image, width, height


    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        # print("bmp:", self.bmp.GetSize())
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        # Get a frame.
        # if capture_library == "opencv":
        #     frame, width, height = self.capture_frame_opencv()
        # elif capture_library == "pygame":
        #     frame, width, height = self.capture_frame_pygame()
        #
        # self.bmp.CopyFromBuffer(frame)

        self.capture_image()


        self.Refresh()

    def capture_image(self):
        # Get a frame.
        if capture_library == "opencv":
            frame, width, height = self.capture_frame_opencv()
            # self.bmp = wx.BitmapFromBuffer(width, height, frame)
            self.bmp.CopyFromBuffer(frame)
        elif capture_library == "pygame":
            frame, width, height = self.capture_frame_pygame()
            self.bmp = frame
        # print(frame.shape)
        # print(width, height)
        # self.bmp = wx.BitmapFromBuffer(width, height, frame)

if __name__ == '__main__':

    if capture_library == "opencv":
        capture = cv2.VideoCapture(0)
    elif capture_library == "pygame":
        pygame.init()
        pygame.camera.init()
        print(pygame.camera.list_cameras())
        cam = pygame.camera.Camera("/dev/video0", (640, 480))
        cam.start()
        i = 0
        while i < 1000000:
            if cam.query_image():
                break
            i += 1
        image = cam.get_image()
        pygame.image.save(image, 'pygame_image.jpeg')
        print(image)
        # display = pygame.display.set_mode((640, 480), 0)
        # display.blit(image, (0, 0))

        capture = cam

    print("Capture/camera:", capture)
    # capture.set(cv2.CV_CAP_PROP_FRAME_WIDTH, 320)
    # capture.set(cv2.CV_CAP_PROP_FRAME_HEIGHT, 240)

    app = wx.App()
    frame = wx.Frame(None)#, size=(640, 480))
    cap = ShowCapture(frame, capture)
    frame.Show()
    app.MainLoop()

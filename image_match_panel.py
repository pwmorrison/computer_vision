import wx

"""
Panel for displaying the matches between two images.
"""

class ImageMatchPanel(wx.Panel):
    def __init__(self, parent, style):
        super(ImageMatchPanel, self).__init__(parent, style=style)
        # Load the image data into a Bitmap
        theBitmap = wx.Bitmap("images/house1_small_corner.jpg")
        # Create a control that can display the
        # bitmap on the screen.
        self.bitmap = wx.StaticBitmap(self, bitmap=theBitmap)
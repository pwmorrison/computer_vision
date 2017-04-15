import wx
from PIL import Image

"""
Panel for displaying the matches between two images.
"""

class ImageMatchPanel(wx.Panel):
    def __init__(self, parent, style, image_path_1, image_path_2):
        super(ImageMatchPanel, self).__init__(parent, style=style)

        if 0:
            # Load the image data into a Bitmap
            theBitmap = wx.Bitmap(image_path_1)

            # Create a control that can display the bitmap on the screen.
            self.bitmap = wx.StaticBitmap(self, bitmap=theBitmap)
        else:
            pilImage = Image.open(image_path_1)
            self.bitmap = self.static_bitmap_from_pil_image(pilImage)

    def static_bitmap_from_pil_image(caller, pil_image):
        """
        From http://stackoverflow.com/questions/39547695/display-pil-image-in-wx-python-in-windows 
        """
        wx_image = wx.EmptyImage(pil_image.size[0], pil_image.size[1])
        wx_image.SetData(pil_image.convert("RGB").tobytes())
        wx_image.SetAlphaData(pil_image.convert("RGBA").tobytes()[3::4])
        bitmap = wx.BitmapFromImage(wx_image)
        static_bitmap = wx.StaticBitmap(caller, wx.ID_ANY, wx.NullBitmap)
        static_bitmap.SetBitmap(bitmap)
        return static_bitmap
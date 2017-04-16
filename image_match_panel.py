import wx
from PIL import Image

"""
Panel for displaying the matches between two images.
"""

class ImageMatchPanel(wx.Panel):
    def __init__(self, parent, style, image_path_1, image_path_2):
        super(ImageMatchPanel, self).__init__(parent, style=style)

        self.im_1 = Image.open(image_path_1)
        self.im_2 = Image.open(image_path_2)

        self.merged_im = self.merge_images(self.im_1, self.im_2)
        self.merged_bitmap = self.static_bitmap_from_pil_image(self.merged_im)

    def merge_images(self, im_1, im_2):

        total_width = im_1.width + im_2.width
        total_height = max([im_1.height, im_2.height])

        new_im = Image.new('RGB', (total_width, total_height))

        new_im.paste(im_1, (0, 0))
        new_im.paste(im_2, (im_1.width, 0))

        return new_im


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
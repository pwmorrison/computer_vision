import wx

class EasyMenu(wx.Menu):
    _map = { wx.ID_CUT : wx.ART_CUT,
    wx.ID_COPY : wx.ART_COPY,
    wx.ID_PASTE : wx.ART_PASTE,
    wx.ID_OPEN : wx.ART_FILE_OPEN,
    wx.ID_SAVE : wx.ART_FILE_SAVE,
    wx.ID_EXIT : wx.ART_QUIT,
    }

    def AddEasyItem(self, id, label=""):
        item = wx.MenuItem(self, id, label)
        art = EasyMenu._map.get(id, None)
        if art is not None:
            bmp = wx.ArtProvider.GetBitmap(art, wx.ART_MENU)
        if bmp.IsOk():
            item.SetBitmap(bmp)
        return self.AppendItem(item)

class ImagePanel(wx.Panel):
    def __init__(self, parent):
        super(ImagePanel, self).__init__(parent)
        # Load the image data into a Bitmap
        theBitmap = wx.Bitmap("images/house1_small_corner.jpg")
        # Create a control that can display the
        # bitmap on the screen.
        self.bitmap = wx.StaticBitmap(self, bitmap=theBitmap)

class MyFrame(wx.Frame):
    def __init__(self, parent, title=""):
        super(MyFrame, self).__init__(parent, title=title)
        # Set an application icon
        # self.SetIcon(wx.Icon("appIcon.png"))
        # Set the panel
        # self.panel = ImagePanel(self)

        # Setup the menus
        menubar = wx.MenuBar()
        self.DoSetupMenus(menubar)
        self.SetMenuBar(menubar)
        # Set the main panel
        self.txt = wx.TextCtrl(self, style=wx.TE_MULTILINE)

    def DoSetupMenus(self, menubar):
        fileMenu = EasyMenu()

        self.RegisterMenuAction(fileMenu, wx.ID_OPEN, self.OnFile)
        self.RegisterMenuAction(fileMenu, wx.ID_SAVE, self.OnFile)
        fileMenu.AppendSeparator()
        self.RegisterMenuAction(fileMenu, wx.ID_EXIT, self.OnFile,
                                "Exit\tCtrl+Q")
        menubar.Append(fileMenu, "File")
        editMenu = EasyMenu()
        self.RegisterMenuAction(editMenu, wx.ID_CUT, self.OnEdit)
        self.RegisterMenuAction(editMenu, wx.ID_COPY, self.OnEdit)
        self.RegisterMenuAction(editMenu, wx.ID_PASTE,
                                self.OnEdit)
        menubar.Append(editMenu, "Edit")

    def RegisterMenuAction(self, menu, id, handler, label=""):
        item = menu.AddEasyItem(id, label)

        self.Bind(wx.EVT_MENU, handler, item)

    def OnFile(self, event):
        if event.Id == wx.ID_OPEN:
            raise NotImplementedError("Open not implemented")

        elif event.Id == wx.ID_SAVE:
            raise NotImplementedError("Save not implemented")
        elif event.Id == wx.ID_EXIT:
            self.Close()
        else:
            event.Skip()

    def OnEdit(self, event):
        action = {wx.ID_CUT: self.txt.Cut,
                  wx.ID_COPY: self.txt.Copy,
                  wx.ID_PASTE: self.txt.Paste}

        if action.has_key(event.Id):
            action.get(event.Id)()
        else:
            event.Skip()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, title="Main Frame")
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
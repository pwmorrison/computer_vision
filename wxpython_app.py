import wx
import images
from image_match_panel import ImageMatchPanel

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


class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID):#, log):
        wx.SplitterWindow.__init__(self, parent, ID,
                                   style=wx.SP_LIVE_UPDATE
                                   )
        # self.log = log

        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashChanged)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnSashChanging)

    def OnSashChanged(self, evt):
        # self.log.WriteText("sash changed to %s\n" % str(evt.GetSashPosition()))
        pass

    def OnSashChanging(self, evt):
        # self.log.WriteText("sash changing to %s\n" % str(evt.GetSashPosition()))
        pass
        # uncomment this to not allow the change
        # evt.SetSashPosition(-1)

TBFLAGS = ( wx.TB_HORIZONTAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            #| wx.TB_TEXT
            #| wx.TB_HORZ_LAYOUT
            )


class SplitterFrame(wx.Frame):
    def __init__(self, parent, title=""):
        super(SplitterFrame, self).__init__(parent, title=title)

        # splitter = MySplitter(nb, -1, log)
        splitter = MySplitter(self, -1)

        # sty = wx.BORDER_NONE
        # sty = wx.BORDER_SIMPLE
        sty = wx.BORDER_SUNKEN

        if 0:
            p1 = wx.Window(splitter, style=sty)
            p1.SetBackgroundColour("pink")
            wx.StaticText(p1, -1, "Panel One", (5, 5))

            p2 = wx.Window(splitter, style=sty)
            p2.SetBackgroundColour("sky blue")
            wx.StaticText(p2, -1, "Panel Two", (5, 5))
        else:
            p1 = ImagePanel(splitter, style=sty)
            p2 = ImagePanel(splitter, style=sty)

        splitter.SetMinimumPaneSize(20)
        splitter.SplitVertically(p1, p2, -100)

        tb = self.CreateToolBar(TBFLAGS)

        # log.write("Default toolbar tool size: %s\n" % tb.GetToolBitmapSize())

        self.CreateStatusBar()

        tsize = (24, 24)
        new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
        open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, tsize)
        paste_bmp = wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, tsize)

        tb.SetToolBitmapSize(tsize)

        # tb.AddSimpleTool(10, new_bmp, "New", "Long help for 'New'")
        tb.AddLabelTool(10, "New", new_bmp, shortHelp="New", longHelp="Long help for 'New'")
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=10)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=10)

        # tb.AddSimpleTool(20, open_bmp, "Open", "Long help for 'Open'")
        tb.AddLabelTool(20, "Open", open_bmp, shortHelp="Open", longHelp="Long help for 'Open'")
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=20)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=20)

        tb.AddSeparator()
        tb.AddSimpleTool(30, copy_bmp, "Copy", "Long help for 'Copy'")
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=30)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=30)

        tb.AddSimpleTool(40, paste_bmp, "Paste", "Long help for 'Paste'")
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=40)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=40)

        tb.AddSeparator()

        # tool = tb.AddCheckTool(50, images.Tog1.GetBitmap(), shortHelp="Toggle this")
        tool = tb.AddCheckLabelTool(50, "Checkable", images.Tog1.GetBitmap(),
                                    shortHelp="Toggle this")
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=50)

        self.Bind(wx.EVT_TOOL_ENTER, self.OnToolEnter)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick)  # Match all
        self.Bind(wx.EVT_TIMER, self.OnClearSB)

        tb.AddSeparator()
        cbID = wx.NewId()

        tb.AddControl(
            wx.ComboBox(
                tb, cbID, "", choices=["", "This", "is a", "wx.ComboBox"],
                size=(150, -1), style=wx.CB_DROPDOWN
            ))
        self.Bind(wx.EVT_COMBOBOX, self.OnCombo, id=cbID)

        tb.AddStretchableSpace()
        # search = TestSearchCtrl(tb, size=(150, -1), doSearch=self.DoSearch)
        # tb.AddControl(search)

        # Final thing to do for a toolbar is call the Realize() method. This
        # causes it to render (more or less, that is).
        tb.Realize()

    def OnToolClick(self, event):
        # self.log.WriteText("tool %s clicked\n" % event.GetId())
        # tb = self.GetToolBar()
        tb = event.GetEventObject()
        tb.EnableTool(10, not tb.GetToolEnabled(10))

    def OnToolRClick(self, event):
        # self.log.WriteText("tool %s right-clicked\n" % event.GetId())
        pass

    def OnCombo(self, event):
        # self.log.WriteText("combobox item selected: %s\n" % event.GetString())
        pass

    def OnToolEnter(self, event):
        # self.log.WriteText('OnToolEnter: %s, %s\n' % (event.GetId(), event.GetInt()))

        # if self.timer is None:
        #     self.timer = wx.Timer(self)
        #
        # if self.timer.IsRunning():
        #     self.timer.Stop()

        # self.timer.Start(2000)
        event.Skip()

    def OnClearSB(self, event):  # called for the timer event handler
        self.SetStatusText("")
        # self.timer.Stop()
        # self.timer = None

    def OnCloseWindow(self, event):
        # if self.timer is not None:
        #     self.timer.Stop()
        #     self.timer = None
        self.Destroy()


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
        # self.txt = wx.TextCtrl(self, style=wx.TE_MULTILINE)

        sty = wx.BORDER_SUNKEN
        self.panel = ImageMatchPanel(self, style=sty)

        if 1:
            tb = self.CreateToolBar(TBFLAGS)

            # log.write("Default toolbar tool size: %s\n" % tb.GetToolBitmapSize())

            self.CreateStatusBar()

            tsize = (24, 24)
            new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
            open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
            copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, tsize)
            paste_bmp = wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, tsize)

            tb.SetToolBitmapSize(tsize)

            # tb.AddSimpleTool(10, new_bmp, "New", "Long help for 'New'")
            tb.AddLabelTool(10, "New", new_bmp, shortHelp="New", longHelp="Long help for 'New'")
            self.Bind(wx.EVT_TOOL, self.OnToolClick, id=10)
            self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=10)

            # tb.AddSimpleTool(20, open_bmp, "Open", "Long help for 'Open'")
            tb.AddLabelTool(20, "Open", open_bmp, shortHelp="Open", longHelp="Long help for 'Open'")
            self.Bind(wx.EVT_TOOL, self.OnToolClick, id=20)
            self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=20)

            tb.AddSeparator()
            tb.AddSimpleTool(30, copy_bmp, "Copy", "Long help for 'Copy'")
            self.Bind(wx.EVT_TOOL, self.OnToolClick, id=30)
            self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=30)

            tb.AddSimpleTool(40, paste_bmp, "Paste", "Long help for 'Paste'")
            self.Bind(wx.EVT_TOOL, self.OnToolClick, id=40)
            self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=40)

            tb.AddSeparator()

            # tool = tb.AddCheckTool(50, images.Tog1.GetBitmap(), shortHelp="Toggle this")
            tool = tb.AddCheckLabelTool(50, "Checkable", images.Tog1.GetBitmap(),
                                        shortHelp="Toggle this")
            self.Bind(wx.EVT_TOOL, self.OnToolClick, id=50)

            self.Bind(wx.EVT_TOOL_ENTER, self.OnToolEnter)
            self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick)  # Match all
            self.Bind(wx.EVT_TIMER, self.OnClearSB)

            tb.AddSeparator()
            cbID = wx.NewId()

            tb.AddControl(
                wx.ComboBox(
                    tb, cbID, "", choices=["", "This", "is a", "wx.ComboBox"],
                    size=(150, -1), style=wx.CB_DROPDOWN
                ))
            self.Bind(wx.EVT_COMBOBOX, self.OnCombo, id=cbID)

            tb.AddStretchableSpace()
            # search = TestSearchCtrl(tb, size=(150, -1), doSearch=self.DoSearch)
            # tb.AddControl(search)

            # Final thing to do for a toolbar is call the Realize() method. This
            # causes it to render (more or less, that is).
            tb.Realize()

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

    def OnToolClick(self, event):
        # self.log.WriteText("tool %s clicked\n" % event.GetId())
        # tb = self.GetToolBar()
        tb = event.GetEventObject()
        tb.EnableTool(10, not tb.GetToolEnabled(10))

    def OnToolRClick(self, event):
        # self.log.WriteText("tool %s right-clicked\n" % event.GetId())
        pass

    def OnCombo(self, event):
        # self.log.WriteText("combobox item selected: %s\n" % event.GetString())
        pass

    def OnToolEnter(self, event):
        # self.log.WriteText('OnToolEnter: %s, %s\n' % (event.GetId(), event.GetInt()))

        # if self.timer is None:
        #     self.timer = wx.Timer(self)
        #
        # if self.timer.IsRunning():
        #     self.timer.Stop()

        # self.timer.Start(2000)
        event.Skip()

    def OnClearSB(self, event):  # called for the timer event handler
        self.SetStatusText("")
        # self.timer.Stop()
        # self.timer = None

    def OnCloseWindow(self, event):
        # if self.timer is not None:
        #     self.timer.Stop()
        #     self.timer = None
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        if 1:
            self.frame = MyFrame(None, title="Main Frame")
        else:
            self.frame = SplitterFrame(None, title="Splitter frame")
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
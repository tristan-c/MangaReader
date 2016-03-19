import wx

def PilImageToWxImage( myPilImage ):
    myWxImage = wx.EmptyImage( myPilImage.size[0], myPilImage.size[1] )
    myWxImage.SetData( myPilImage.convert( 'RGB' ).tostring() )
    return myWxImage

def PilImageToWxBitmap( myPilImage ) :
    return wx.Bitmap(PilImageToWxImage( myPilImage ))


class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent, -1)

        self.image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(400,400))
        self.bitmap = None

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add((1,1),1)
        sizer.Add(self.image, 0, wx.ALIGN_CENTER | wx.ALL | wx.ADJUST_MINSIZE, 10)
        sizer.Add((1,1),1)

        self.SetSizer(sizer)
        sizer.Fit(parent)

        self.SetBackgroundColour('BLACK')

        self.Bind(wx.EVT_LEFT_UP, self.next)
        self.Bind(wx.EVT_RIGHT_UP, self.previous )
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.image.Bind(wx.EVT_LEFT_UP, self.next)
        self.image.Bind(wx.EVT_RIGHT_UP, self.previous )

    def next(self,event):
        print("next")
        self.bitmap = wx.Bitmap('/home/illusive/1ccc123e03cbe0ae97bcd9ed42e04a79.jpg')
        bitmap = self.scale_bitmap(self.bitmap)
        self.image.SetBitmap(bitmap) 

    def previous(self,event):
        print("previous")

    def on_size(self,event):
        if self.bitmap == None:
            return

        bitmap = self.scale_bitmap(self.bitmap)
        self.image.SetBitmap(bitmap)
        self.Layout()

    def scale_bitmap(self,bitmap):
        image = bitmap.ConvertToImage()
        image_width = image.GetWidth()
        image_height = image.GetHeight()

        max_width,max_height = self.GetSize()

        ratio = min(max_width/image_width, max_height/image_height)

        new_width = image_width * ratio
        new_height = image_height * ratio


        image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image)

class Application_window(wx.Frame):
    
    def __init__(self, parent, title):
        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(500,500))
        self.Center()
        
        self.dirname=''
        self.SetBackgroundColour('BLACK')
        self.InitUI()
        
    def InitUI(self):    

        # Setting up the menu.
        # filemenu= wx.Menu()
        # menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        # menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        # menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Events.
        # self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        # self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        # self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

        # Creating the menubar.
        # menuBar = wx.MenuBar()
        # menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        # self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        toolbar = self.CreateToolBar()
        qtool = toolbar.AddTool(wx.ID_ANY, 'Quit', wx.Bitmap('next.png'))
        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.OnExit, qtool)

        self.SetSize((250, 200))
        self.SetTitle('Simple toolbar')
        self.Centre()
        self.Show(True)

        panel = Panel(self)
        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(panel, 1, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

        self.Bind(wx.EVT_MOUSEWHEEL , self.derp, self)
        

    def derp(self,t):
        print(t)
        
    # def OnAbout(self,e):
    #     # Create a message dialog box
    #     dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
    #     dlg.ShowModal() # Shows it
    #     dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

    # def OnOpen(self,e):
    #     """ Open a file"""
    #     dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
    #     if dlg.ShowModal() == wx.ID_OK:
    #         self.filename = dlg.GetFilename()
    #         self.dirname = dlg.GetDirectory()
    #         f = open(os.path.join(self.dirname, self.filename), 'r')
    #         self.control.SetValue(f.read())
    #         f.close()
    #     dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    Application_window(None,"reader")
    app.MainLoop()
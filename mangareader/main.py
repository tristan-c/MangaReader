
from os import listdir
from os.path import expanduser, dirname, isfile, join, basename
from time import time

import wx
from PIL import Image
from PIL.Image import ANTIALIAS

from archive_manager import ArchiveManager

def PilImageToWxImage( myPilImage ):
    myWxImage = wx.Image( myPilImage.size[0], myPilImage.size[1] )
    myWxImage.SetData( myPilImage.convert( 'RGB' ).tobytes())
    return myWxImage

def PilImageToWxBitmap( myPilImage ) :
    return wx.Bitmap(PilImageToWxImage( myPilImage ))


class Panel(wx.Panel):
    def __init__(self, parent):
        super(Panel, self).__init__(parent, -1)

        self.image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(400,400))
        self.pil_image = None

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

        self.repeat_key = 0
        self.last_action_ts = time()

    def load_first_page(self):
        _file = self.Parent.archive_manager.first_page()
        if _file:
            self.set_image(_file)

    def load_last_page(self):
        _file = self.Parent.archive_manager.last_page()
        if _file:
            self.set_image(_file)

    def next(self,event):
        if self.Parent.current_archive:
            _file = self.Parent.archive_manager.next()
            self.display_page(_file)

    def previous(self,event):
        if self.Parent.current_archive:
            _file = self.Parent.archive_manager.previous()
            self.display_page(_file,next_file=False)

    def display_page(self,_file,next_file=True):
        if _file:
            self.set_image(_file)
            self.last_action_ts = time()
        else:
            if self.repeat_key >= 2:
                delay = time() - self.last_action_ts 
                if delay >= 1: 
                    if not next_file:
                        self.Parent.change_archive(next_file,first_page=False)
                    else:
                        self.Parent.change_archive(next_file)
                self.repeat_key = 0
            else:
                self.repeat_key += 1

    def set_image(self,bytes_image):
        self.pil_image = Image.open(bytes_image)
        bitmap = self.scale_bitmap(self.pil_image)
        bitmap = PilImageToWxBitmap(bitmap)
        self.image.SetBitmap(bitmap)
        self.Layout()

    def on_size(self,event):
        if self.pil_image == None:
            return

        bitmap = self.scale_bitmap(self.pil_image)
        bitmap = PilImageToWxBitmap(bitmap)
        self.image.SetBitmap(bitmap)
        self.Layout()

    def scale_bitmap(self,image):
        image_width,image_height = image.size
        max_width,max_height = self.GetSize()

        ratio = min(max_width/image_width, max_height/image_height)

        new_width = int(image_width * ratio)
        new_height = int(image_height * ratio)

        image = image.resize((new_width, new_height), ANTIALIAS)

        return image

class Application_window(wx.Frame):
    
    def __init__(self, parent, title):

        self.archive_manager = ArchiveManager()
        self.wildcard = "Zip archive (*.zip)|*.zip|"\
                        "Tar acrhive (*.tar)|*.tar"


        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(500,500))
        self.Center()
        
        self.dirname=expanduser("~")
        self.SetBackgroundColour('BLACK')

        self.panel = Panel(self)
        # Use some sizers to see layout options
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel, 1, wx.EXPAND)

        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show()

        self.InitUI()
        
    def InitUI(self):
        toolbar = self.CreateToolBar()

        tool_open = toolbar.AddTool(wx.ID_ANY, 'Open', wx.Bitmap('icons/Home.png'))
        tool_first = toolbar.AddTool(wx.ID_ANY, 'Previous archive', wx.Bitmap('icons/First.png'))
        tool_previous = toolbar.AddTool(wx.ID_ANY, 'Previous', wx.Bitmap('icons/Previous.png'))
        tool_next = toolbar.AddTool(wx.ID_ANY, 'Next', wx.Bitmap('icons/Next.png'))
        tool_last = toolbar.AddTool(wx.ID_ANY, 'Next archive', wx.Bitmap('icons/Last.png'))

        toolbar.Realize()

        self.Bind(wx.EVT_TOOL, self.on_open, tool_open)
        self.Bind(wx.EVT_TOOL, self.panel.previous, tool_previous)
        self.Bind(wx.EVT_TOOL, self.panel.next, tool_next)
        self.Bind(wx.EVT_TOOL, self.previous_archive, tool_first)
        self.Bind(wx.EVT_TOOL, self.next_archive, tool_last)
        #
        self.Bind(wx.EVT_MOUSEWHEEL , self.dispatch_mouse, self)

        self.SetSize((600, 600))
        self.SetTitle('Comic reader')
        self.Centre()
        self.Show(True)

        self.current_archive = None

    def dispatch_mouse(self,event):
        if event.GetWheelRotation() > 0:
            self.panel.next(event)
        else:
            self.panel.previous(event)
        
    # def OnAbout(self,e):
    #     # Create a message dialog box
    #     dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
    #     dlg.ShowModal() # Shows it
    #     dlg.Destroy() # finally destroy it when finished.
    def next_archive(self,e):
        self.change_archive()

    def previous_archive(self,e):
        self.change_archive(next_archive=False)

    def on_open(self,e=None):
        """ Open a file"""
        openFileDialog = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return  

        try:
            f = open(openFileDialog.GetPath(), 'r')
            f.close()
        except Exception as e:
            wx.LogError("Cannot open file '%s' : %s." % (openFileDialog.GetPath(),str(e)))
            return

        self.open_archive(openFileDialog.GetPath())

    def change_archive(self, next_archive=True, first_page=True):
        if self.current_archive:
            file_list = []

            for f in listdir(self.dirname):
                filename = join(self.dirname, f)
                if isfile(filename):
                    file_list.append(filename)

            files = sorted(file_list)
            index = files.index(self.current_archive)
            index = index + 1 if next_archive else index -1

            # if -1 we're a the start of directory, prevent looping to the end
            if index < 0:
                return 

            if index < len(files):
                self.open_archive(files[index],first_page=first_page)

    def open_archive(self,path, first_page=True):
        self.current_archive = path
        self.dirname = dirname(path)

        self.archive_manager.open_zip(path)

        self.SetTitle(basename(self.current_archive))

        if first_page:
            self.panel.load_first_page()
        else:
            self.panel.load_last_page()


if __name__ == '__main__':
    app = wx.App()
    Application_window(None,"mangareader")
    app.MainLoop()
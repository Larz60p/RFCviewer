"""
Copyright (c) 2017 Larz60+

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

===== Notes for this program =====

RFC file formats: There are four possibilities one or all mey be present, txt. pdf, xml, and/or html

Please see the page on documentation retrieval here: https://www.rfc-editor.org/retrieve/

Scrape this site for bulk download see page details in data/https _www.rfc-editor.org_retrieve_bulk_.htm
    For text:
         entire zip file here: https://www.rfc-editor.org/in-notes/tar/RFC-all.zip
         entire tar file here: https://www.rfc-editor.org/in-notes/tar/RFCs0001-0500.tar.gz
    PDF:
         entire zip file here: https://www.rfc-editor.org/in-notes/tar/pdfrfc0001-0500.zip
         entire tar file here: https://www.rfc-editor.org/in-notes/tar/pdfrfc-all.tar.gz
"""
import wx
import wx.aui
import ExtractRFC


class RFCviewer(wx.Frame):

    def __init__(self, parent, id=-1, title='RFC Document Viewer',
                 pos=wx.DefaultPosition, size=(1000, 700),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)

        # create several text controls
        # Create a lef panel as a container for the ListCtrl and search box
        
        self.left_panel = wx.Panel()
        self.rfc_list = wx.ListCtrl(self, id=wx.ID_ANY,
                                    pos=wx.DefaultPosition,
                                    size=wx.Size(200,150),
                                    style=wx.NO_BORDER | wx.TE_MULTILINE,
                                    name='rfc_list')

        self.search = wx.SearchCtrl(self, size=(200, -1), style=wx.TE_PROCESS_ENTER)

        misc_text = wx.TextCtrl(self, -1, 'What to do with this space?',
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        self.nb = wx.aui.AuiNotebook(self,
                                     id=wx.ID_ANY,
                                     pos=wx.DefaultPosition,
                                     size=wx.Size(200,150),
                                     style=wx.aui.AUI_NB_DEFAULT_STYLE)

        page1 = wx.TextCtrl(self.nb,
                           id=wx.ID_ANY,
                           pos=wx.DefaultPosition,
                           size=wx.Size(200,150),
                           style=wx.TE_MULTILINE)

        self.nb.AddPage(page1, "RFC Document Summary")

        page2 = wx.TextCtrl(self.nb, -1,
                           style=wx.TE_MULTILINE)
        self.nb.AddPage(page2, "RFC Document Detail")

        page3 = wx.TextCtrl(self.nb, -1,
                           style=wx.TE_MULTILINE)
        self.nb.AddPage(page3, "Update Manager")

        # add the panes to the manager
        info = wx.aui.AuiPaneInfo()
        info.Caption('RFC Document Selection')
        info.CaptionVisible(True)
        info.Left()
        info.Dockable(True)
        info.Name('self.rfc_list')
        self._mgr.AddPane(self.rfc_list, info)

        info = wx.aui.AuiPaneInfo()
        info.CaptionVisible(False)
        info.Left()
        info.Dockable(False)
        info.Name('self.search')
        self._mgr.AddPane(self.search, info)

        info = wx.aui.AuiPaneInfo()
        info.Caption('Extra space - May delete if not needed')
        info.CaptionVisible(True)
        info.Bottom()
        info.Dockable(True)
        info.Name('misc_text')
        self._mgr.AddPane(misc_text, info)

        info = wx.aui.AuiPaneInfo()
        info.CaptionVisible(False)
        info.Center()
        info.Dockable(True)
        info.Name('nb')
        self._mgr.AddPane(self.nb, info)

        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(self.rfc_list, 2, wx.EXPAND)
        # sizer.Add(self.search, 1, wx.EXPAND)
        # self.SetSizer(sizer)
        # # wx.CallAfter(nb.SendSizeEvent)

        self.count = 0
        mb = self.MakeMenuBar()
        self.SetMenuBar(mb)
        self.CreateStatusBar()

        self.crfc_index = 0
        self.rfc_list.InsertColumn(col=0, heading="RFC Id", format=wx.LIST_FORMAT_LEFT, width=60)
        self.rfc_list.InsertColumn(col=1, heading="RFC Title", format=wx.LIST_FORMAT_LEFT, width=800)

        self.load_rfc_entries()

        self._mgr.GetPane("rfc_list").dock_proportion = 1
        self._mgr.GetPane("rfc_list").dock_proportion = 3
        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        # # rfc_list_proportions = GetTotalPixSizeAndProportion(self, self.rfc_list)
        # totalPixsize, totalProportion = wx.aui.GetTotalPixSizeAndProportion(self.rfc_list)
        # print('rfc_list totalPixsize: {}, totalProportion: {}'.format(totalPixsize, totalProportion))
        #
        # totalPixsize, totalProportion = wx.aui.GetTotalPixSizeAndProportion(self.nb)
        # print('nb totalPixsize: {}, totalProportion: {}'.format(totalPixsize, totalProportion))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def load_rfc_entries(self):
        exrfc = ExtractRFC.ExtractRFC(local=True)

        if exrfc.index_loaded:
            self.rfc_index = exrfc.rfc_index
            self.index_loaded = True
        else:
            ErrorMsg(self, 'Please start internetwork and restart', 'ExtractRFC')

        for key, value in self.rfc_index.items():
            title = self.rfc_index[key]['title']
            self.rfc_list.InsertItem(self.crfc_index, key)
            self.rfc_list.SetItem(self.crfc_index, 1, title)
            self.crfc_index += 1

    def document_summary(self, nb):
        pass

    def document_detail(self, nb):
        pass

    def spare(self, nb):
        pass

    def MakeMenuBar(self):
        mb = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(-1, "New child window\tCtrl-N")
        self.Bind(wx.EVT_MENU, self.OnNewChild, item)
        item = menu.Append(-1, "Close parent")
        self.Bind(wx.EVT_MENU, self.OnClose, item)
        mb.Append(menu, "&File")
        return mb

    def OnNewChild(self, evt):
        self.count += 1
        child = ChildFrame(self, self.count)
        child.Show()

    def OnClose(self, event):
        for m in self.GetChildren():
            if isinstance(m, wx.aui.AuiMDIClientWindow):
                for k in m.GetChildren():
                    if isinstance(k, ChildFrame):
                        k.Close()
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()

def main():
    app = wx.App()
    frame = RFCviewer(None)
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()

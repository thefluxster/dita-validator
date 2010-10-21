#!/usr/bin/env python
"""
stext.py

StaticWrapText wxPython widget; implements StaticText widget with basic word
wrapping algorithm to support intelligent resizing.
"""

__id__ = "$Id: stext.py,v 1.1 2004/09/15 16:45:55 nyergler Exp $"
__version__ = "$Revision: 1.1 $"
__copyright__ = '(c) 2004, Nathan R. Yergler'
__license__ = 'licensed under the GNU GPL2'

import wx
import wx.xrc

class StaticWrapTextXmlHandler(wx.xrc.XmlResourceHandler):
    def __init__(self):
        wx.xrc.XmlResourceHandler.__init__(self)
        
        # Specify the styles recognized by objects of this type
        self.AddStyle("wx.NO_3D", wx.NO_3D)
        self.AddStyle("wx.TAB_TRAVERSAL", wx.TAB_TRAVERSAL);
        self.AddStyle("wx.WS_EX_VALIDATE_RECURSIVELY",
                      wx.WS_EX_VALIDATE_RECURSIVELY);
        self.AddStyle("wx.CLIP_CHILDREN", wx.CLIP_CHILDREN);

        self.AddWindowStyles()

    def CanHandle(self, node):
        return self.IsOfClass(node, "StaticWrapText")

    def DoCreateResource(self):
        # we only currently support creation from scratch
        assert self.GetInstance() is None
 
        # create the new instance and return it
        swt = StaticWrapText(self.GetParentAsWindow(),
                              self.GetID(),
                              self.GetText('label'),
                              self.GetPosition(),
                              self.GetSize(),
                              self.GetStyle("style", wx.TAB_TRAVERSAL),
                              self.GetName(),
                              )
        return swt

class StaticWrapText(wx.StaticText):
    """A StaticText-like widget which implements word wrapping."""
    
    def __init__(self, *args, **kwargs):
        wx.StaticText.__init__(self, *args, **kwargs)

        # store the initial label
        self.__label = super(StaticWrapText, self).GetLabel()

        # listen for sizing events
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def SetLabel(self, newLabel):
        """Store the new label and recalculate the wrapped version."""
        self.__label = newLabel
        self.__wrap()

    def GetLabel(self):
        """Returns the label (unwrapped)."""
        return self.__label
    
    def __wrap(self):
        """Wraps the words in label."""
        words = self.__label.split()
        lines = []

        # get the maximum width (that of our parent)
        max_width = self.GetParent().GetVirtualSizeTuple()[0]
        
        index = 0
        current = []

        for word in words:
            current.append(word)

            if self.GetTextExtent(" ".join(current))[0] > max_width:
                del current[-1]
                lines.append(" ".join(current))

                current = [word]

        # pick up the last line of text
        lines.append(" ".join(current))

        # set the actual label property to the wrapped version
        super(StaticWrapText, self).SetLabel("\n".join(lines))

        # refresh the widget
        self.Refresh()
        
    def OnSize(self, event):
        # dispatch to the wrap method which will 
        # determine if any changes are needed
        self.__wrap()
            
if __name__ == '__main__':
    # if executed as a script, demonstrate use of the StaticWrapText widget
    # from an XRC resource, in this case a string (stext_xrc)
    
    stext_xrc = """<?xml version="1.0" ?>
<resource>
  <object class="wxFrame" name="FRAME1">
    <title></title>
    <object class="wxGridBagSizer">
      <object class="sizeritem">
        <object class="StaticWrapText" name="SWT_TEST">
          <label>This is a test of word wrapping in an XML-generated StaticWrapText.</label>
        </object>
        <flag>wxALL|wxEXPAND</flag>
        <minsize>0,0</minsize>
        <cellpos>0,0</cellpos>
        <cellspan>1,1</cellspan>
      </object>
      <vgap>10</vgap>
      <hgap>100</hgap>
      <growablecols>0</growablecols>
      <growablerows>0</growablerows>
    </object>
  </object>
</resource>
"""
      
    # create a simple frame for testing
    app = wx.PySimpleApp()

    # Load the XRC resource
    res = wx.xrc.EmptyXmlResource()
    res.InsertHandler(StaticWrapTextXmlHandler())
    res.LoadFromString(stext_xrc)

    main = res.LoadFrame(None, 'FRAME1')
    
    main.Show()
    app.MainLoop()

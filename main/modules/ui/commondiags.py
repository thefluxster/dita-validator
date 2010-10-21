#!/usr/bin/python -u
import wx
import os

# File dialogs:
def open_it(parentdialog):
    #application = wx.PySimpleApp()
    # Create an open file dialog
    newdialog = wx.FileDialog (parentdialog, style = wx.OPEN)    
    # Show the dialog and get user input
    filename = ""
    
    if newdialog.ShowModal() == wx.ID_OK:
        filename = newdialog.GetPath()
    # The user did not select anything
    else:
        print 'Nothing was selected.'
    # Destroy the dialog
    newdialog.Destroy()
    #application.Exit()
    return filename

def open_folder(parentdialog, defaultpath = ""):
    #application = wx.PySimpleApp()
    # Create an open file dialog
    if os.path.exists(defaultpath):
        newdialog = wx.DirDialog(parentdialog, defaultPath=defaultpath, style = wx.OPEN)
    else:
        newdialog = wx.DirDialog(parentdialog, style = wx.OPEN)
    # Show the dialog and get user input
    folder = ""
    if newdialog.ShowModal() == wx.ID_OK:
        folder = newdialog.GetPath()
    # The user did not select anything
    else:
        print 'Nothing was selected.'
    # Destroy the dialog
    newdialog.Destroy()    
    #application.Exit()
    return folder
    
def save_it(parentdialog):
    #application = wx.PySimpleApp()
    # Create an open file dialog
    newdialog = wx.FileDialog (parentdialog, style = wx.SAVE)
    # Show the dialog and get user input    
    filename = ""
    if newdialog.ShowModal() == wx.ID_OK:
        filename = newdialog.GetPath()
    # The user did not select anything
    else:
        print 'Nothing was selected.'
    # Destroy the dialog
    newdialog.Destroy()
    #application.Exit()
    return filename
    
def save_as(parentdialog):
    #application = wx.PySimpleApp()
    # Create an open file dialog
    newdialog = wx.FileDialog (parentdialog, style = wx.SaveFileSelector)    
    # Show the dialog and get user input
    filename = ""
    if newdialog.ShowModal() == wx.ID_OK:
        filename = newdialog.GetPath()
    # The user did not select anything
    else:
        print 'Nothing was selected.'
    # Destroy the dialog
    newdialog.Destroy()
    #application.Exit()
    return filename

#Message Dialogs

def ShowWarning(parent, title, message):
    #Dialog to show a warning
    #application = wx.PySimpleApp()
    dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.ICON_ERROR)    
    newval = False
    if dlg.ShowModal() == wx.OK:
        newval = True
    dlg.Destroy()
    #application.Exit()
    return newval
    
def ShowInfo(parent, title, message):
    #dialog to show information
    #application = wx.PySimpleApp()
    dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.ICON_INFORMATION)
    
    newval = False
    if dlg.ShowModal() == wx.OK:
        newval = True
    dlg.Destroy()
    #application.Exit()
    return newval
    
def ShowYesNoQuestion(parent, title, question):
    #dialog to ask a yes or now question
    #application = wx.PySimpleApp()
    dlg = wx.MessageDialog(parent, question, title, wx.YES_NO | wx.ICON_QUESTION)
    
    newval = False
    if dlg.ShowModal() == wx.ID_YES:
        newval = True
    else:
        newvale = False
    dlg.Destroy()
    #application.Exit()
    return newval
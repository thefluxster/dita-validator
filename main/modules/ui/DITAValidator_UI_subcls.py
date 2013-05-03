#!/usr/bin/env python
import os
import sys
import stat

import DITAValidator_UI
import commondiags
from modules.proc import validatexml
from modules.common import version
from modules.common import commonfuncs


class DITAValidatorSub(DITAValidator_UI.SimpleFrame):
    def UserOptions(self):
        self.text_ctrlCatalog.SetValue(os.path.join("dtds", "catalog-dita.xml"))
        self.SetMinSize((890,612))
        self.SetSize((890,612))
        self.checkboxCleanNestedTCs.SetLabel("Clean nested tracked changes")
        self.checkboxTrimIXTermSpaces.SetLabel("Delete extra spaces from <indexterms>")
        self.checkboxInsertIXSortAs.SetLabel("Insert <index-sort-as> elements")
        self.checkboxAcceptTCs.SetLabel("Tracked Changes: Accept All")
        self.checkboxMoveUISpaces.SetLabel("For <uicontrol> and <cite>, move spaces outside tags")
        self.checkboxDelMenuCSpacs.SetLabel("Delete spaces from <menucascade>")        
        self.labelVersion.SetLabel("Version: %s" % version.version)        
    
    def OnBrowseCatalog(self, event): # wxGlade: SimpleFrame.<event_handler>
        #print "Event handler `OnBrowseCatalog' not implemented!"
        #event.Skip()
        newpath = commondiags.open_it(self)
        if newpath != "":
            self.text_ctrlCatalog.SetValue(newpath)
        event.Skip()
            
    def OnBrowseDITAMap(self, event): # wxGlade: SimpleFrame.<event_handler>
        curinputtype = self.choiceInputType.GetCurrentSelection()
        
        if curinputtype == 0:            
            newpath = commondiags.open_it(self)
        elif curinputtype == 1:
            currentinput = self.text_ctrlDITAMap.Value            
            newpath = commondiags.open_folder(self, currentinput)        
        if newpath != "":
            self.text_ctrlDITAMap.SetValue(newpath)
        event.Skip()
        
    def OnBrowseOutput(self, event): # wxGlade: SimpleFrame.<event_handler>
        #print "Event handler `OnBrowseOutput' not implemented!"
        #event.Skip()
        newpath = commondiags.open_folder(self)
        if newpath != "":
            self.text_ctrlOutput.SetValue(newpath)
        event.Skip()
        
    def OnStart(self, event): # wxGlade: SimpleFrame.<event_handler>
        #Run checks to ensure we have the proper content we need.
        catalogpath = self.text_ctrlCatalog.GetValue()
        if not catalogpath[1:3] == ":\\":
            if os.name == "nt":
                if os.path.exists("c:\\Program Files\\Example\\DITAValidator"):
                    progpath = "c:\\Program Files\\Example\\DITAValidator"
                else:
                    progpath = "c:\\Program Files (x86)\\Example\\DITAValidator"                    
                os.chdir(progpath)
            if os.path.exists(os.path.join(os.getcwd(), catalogpath)):
                catalogpath = os.path.join(os.getcwd(), catalogpath)
            else:
                catalogpath = os.path.join(os.getcwd(), "dist", catalogpath)        
            
        if os.path.exists(catalogpath) and os.path.exists(self.text_ctrlDITAMap.GetValue()):
            validationresults = ""
            self.text_ctrlMessageReport.SetValue("Processing...")            
            self.frame_1_statusbar.SetStatusText("Processing...")
            
            myvalidator = validatexml.clsValidateXML(self.text_ctrlDITAMap.GetValue(), catalogpath)
            validationresults = myvalidator.start()            
            #Get the current timestamp for the log:
            mytime = commonfuncs.GetTextTimeStamp()
            validationresults = mytime + os.linesep + "Validation complete.  Issues reported during validation check:" + os.linesep + validationresults
            
            #Print to the dialog:
            self.text_ctrlMessageReport.SetValue(validationresults)
            
            
            #Print to the log:
            if os.path.exists(os.path.join(os.path.dirname(self.text_ctrlDITAMap.GetValue()), "validation.log")): #check to see if the log already exists
                os.chmod(os.path.join(os.path.dirname(self.text_ctrlDITAMap.GetValue()), "validation.log"), stat.S_IWRITE) #make file writable
                os.remove(os.path.join(os.path.dirname(self.text_ctrlDITAMap.GetValue()), "validation.log")) #delete it
            logfile = open(os.path.join(os.path.dirname(self.text_ctrlDITAMap.GetValue()), "validation.log"), mode='w')
            logfile.write(validationresults)
            logfile.close()
            self.frame_1_statusbar.SetStatusText("Ready")            
            myvalidator = None
        else:
            commondiags.ShowWarning(self, "Invalid Path(s)", "One or more input file paths are invalid.")
        event.Skip()
        
    def OnReset(self, event): # wxGlade: SimpleFrame.<event_handler>
        self.ResetAllFields()
        event.Skip()
        
    def OnHelp(self, event): # wxGlade: SimpleFrame.<event_handler>
        self.text_ctrlMessageReport.AppendText(os.linesep + os.linesep + "No help available.  Contact <ditasupport@example.com>.")
        event.Skip()

    def OnExit(self, event): # wxGlade: SimpleFrame.<event_handler>
        self.Close()
        self.Destroy()
        sys.exit()
    def OnInputType(self, event): # wxGlade: SimpleFrame.<event_handler>
        cursel = self.choiceInputType.GetCurrentSelection()
        if cursel == 0:
            #user chose to input a ditamap:
            self.labelInput.SetLabel("DITA Map:")
        elif cursel == 1:
            #user chose to input a directory:
            self.labelInput.SetLabel(" Directory:")
        event.Skip()
        
        
    def ResetAllFields(self):
        self.text_ctrlCatalog.SetValue("")
        self.text_ctrlDITAMap.SetValue("")
        self.text_ctrlOutput.SetValue("")        
        self.combo_boxEncoding.SetSelection(0)

#!/usr/bin/env python

import sys
import os
import stat
import string
import getopt
import wx

from modules.proc import validatexml
from modules.proc import copydita
from modules.proc import cleandita
from modules.help import usage
from modules.proc import ditaproc
from modules.common import msghandler
from modules.common import commonfuncs
from modules.common import version
from modules.ui import DITAValidator_UI_subcls

def main(argv):
    #Global vars:
    global _useGUI
    global _debug
    global _encoding
    global _catalog
    global _mastermap
    global _indexsortas
    global _acceptchanges
    global _remnestedchanges
    global _outputdir
    global _properties
    global _rmwhitespace
    
    
    
    #set defaults:
    _useGUI = False
    _debug = "4"
    _encoding = "utf-16"
    #Packaged Catalog
    _catalog = os.path.join("dtds","catalog-dita.xml")
    #Sample ditamap
    __samplepath__ = os.path.join(os.path.normpath(os.path.curdir), "samples")
    _mastermap = os.path.join(__samplepath__,"test_a_super_long_name_ditamap_with_no_business_being_this_long_at_all_my_friends.ditamap")
    
    _indexsortas = False
    _acceptchanges = False
    _remnestedchanges = False
    _outputdir = ""
    _properties = False
    _rmwhitespace = False
    
    if argv == []:
        #if we have no args, we're using GUI for this session.
        _useGUI = True
    else:
        #If there are values in argv, let's get our options:
        
        try:                                
            opts, args = getopt.getopt(argv, "he:i:aro:pwc:d:", ["help", "encoding=", "map=", "acceptchanges", "remnestedchanges", "outputdir=", "properties", "rmwhitespace", "catalog=", "debug="]) 
        except getopt.GetoptError:           
            usage.usage()                          
            sys.exit(2)                     
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage.usage()
                sys.exit()
            elif opt in ("-e", "--encoding"):
                #make sure the user didn't leave off the value...
                if arg[0] == "-":
                    usage.usage()
                    sys.exit(2) 
                _debug = arg            
            elif opt in ("-i", "--map"):
                #make sure the user didn't leave off the value...
                if arg[0] == "-":
                    usage.usage()
                    sys.exit(2)                 
                _mastermap = arg
            elif opt in ("-a", "--acceptchanges"):
                _acceptchanges = True
            elif opt in ("-r", "--remnestedchanges"):
                _remnestedchanges = True
            elif opt in ("-o", "--outputdir"):
                #make sure the user didn't leave off the value...
                if arg[0] == "-":
                    usage.usage()
                    sys.exit(2) 
                _outputdir = arg
            elif opt in ("-p", "--properties"):
                _properties = True
            elif opt in ("-w", "--rmwhitespace"):
                _rmwhitespace = True            
            elif opt in ("-c", "--catalog"):
                #make sure the user didn't leave off the value...
                if arg[0] == "-":
                    usage.usage()
                    sys.exit(2)
                _catalog = arg
            elif opt in ("-d", "--debug"):
                if arg:
                    _debug = arg
                else:
                    _debug = "4"
            
    #If useGUI, we weren't given any options and need to gather them later.
    #We'll do more with the options we've gathered later.  
    #For now, if we have our args, launch the validator via the ditavalidator.py module
    if argv != []:
        print "DITA Validator " + version.version
        mymap = _mastermap
        mycatalog = _catalog
        myvalidator = validatexml.clsValidateXML(mymap, mycatalog)
        validationresults = myvalidator.start(_debug)        
        validationresults = commonfuncs.GetTextTimeStamp() + validationresults
        print "Validation complete.  Issues reported during validation check:"
        print validationresults
        #Print to the log:
        if os.path.exists(os.path.join(os.path.dirname(mymap), "validation.log")): #check to see if the log already exists            
            os.chmod(os.path.join(os.path.dirname(mymap), "validation.log"), stat.S_IWRITE) #make file writable
            os.remove(os.path.join(os.path.dirname(mymap), "validation.log")) #delete it
        logfile = open(os.path.join(os.path.dirname(mymap), "validation.log"), mode='w')
        logfile.write(validationresults)
        logfile.close()
        sys.exit(msghandler.errorsObj.exitcode)
    else:
        #Get input from GUI as args[] and then launch validator module via the GUI.
        app = wx.PySimpleApp(0)
        wx.InitAllImageHandlers()
        frame_1 = DITAValidator_UI_subcls.DITAValidatorSub(None, -1, "")
        app.SetTopWindow(frame_1)
        frame_1.Show()
        app.MainLoop()
        
if __name__ == "__main__":
    main(sys.argv[1:])
#!/usr/bin/env python

import os

#Note that the DITATopic object is a misnomer since topics and maps can be stored as DITATopic objects
class DITATopicInfo():
        # Absolute path to the DITA topic or map file
        strFilePath = ""
        # Set up a Dirty flag in case derived objects need to mark an individual topic as dirty
        blnDirty = False
        # Indicates if the file is writable
        blnReadOnlyFile = False
        # Provide the relative path from the map (or just the filename if it's in the same directory as the map that links to it)
        strShortFilePath = ""

        def __init__(self, strTopicFilePath = "", strMapPath=""):
                # Set up the new object
                self.strFilePath = strTopicFilePath
                # Truncate the path using the Map Path
                self.strShortFilePath = strTopicFilePath.replace(strMapPath, "")
                self.blnDirty = False
                # Need to check if the file is writable
                self.blnReadOnlyFile = self.__FileIsReadOnly__(self.strFilePath)
        
        def __FileIsReadOnly__(self, strURI):
                # Use the file system object to check whether the file is readonly
                if os.access(strURI, os.R_OK):
                        return True
                else:
                        return False
                
#!/usr/bin/env python

import sys
import os
import string
import StringIO
from lxml import etree
from xml.dom import minidom
import lxml

from modules.common import commonfuncs
import findenc
from modules.common import msghandler
import clsDITATopicInfo

moduleName = "ditaProc"

class processEngineClass():
    
    

    class LinkFileStructure():
            strAbsPath = "" #Absolute path to the file
            strScope = "" #When applicable
            strLinkedCurrentFileAs = "" #Conref, xref, href, etc.
            
    class processDictionaries():
        #The FileHash contains all referenced DITA topics and maps using their path as a unique look up key
        dictFileHash = {}
        dictImageHash = {}
        dictConrefHash = {}
        dictExternalXrefHash = {}
        dictInternalXrefHash = {}
        dictTopicRefHash = {}
    
    #Class Variables and Objects    
    _testmsgs = ""
    ResultsDicts = processDictionaries()
    strOutputType = ""
    #This gets overridden if the user has created one of the subclasses based on this class.
    pathtocatalog = os.path.join("dtds","catalog-dita.xml")    
    
    #internal vars (mainly for unit testing)
    __samplepath__ = os.path.join(os.path.normpath(os.path.curdir), "samples")
    __mypathtoxml__ = os.path.join(__samplepath__,"mainmap.ditamap")
    
    def __init__(self):
        pass


    
    def GetAppleHelpImages(self, xmldocument, dictCurDict={}, strXPath = "//", pathtofile = ""):
        href = ""
        folder = os.path.dirname(pathtofile)
        #Create a function to store our xpath:
        xpatherator = etree.XPath(strXPath)
        matchedattributes = xpatherator(xmldocument)
        
        for c in matchedattributes:
            href = c
            #if the first character is # then we have this is an internal xref and we don't need to process it further.
            if href.startswith("#"):
                continue
            href = href.split("#")[0]
            #Build out an absolute URL by combining the current folder path and the href (note: may contain ../)
            href = os.path.join(folder, href)
            #Check to see if the file already exists in the hash table before adding it
            if not dictCurDict.has_key(href):
                dictCurDict[href] = clsDITATopicInfo.DITATopicInfo(href, folder)
            
            try:
                if not os.path.exists(os.path.normpath(href)):
                    msghandler.errorsObj.PrintMessage(3, pathtofile + " references a non-existing file: " + href, moduleName + "-DITAproc-GetAppleHelpImages")
            except Exception, e:
                # store the message in our error obj:
                msghandler.errorsObj.PrintMessage(3, "Unpredicted error while processing: " + href + ". Message: " + str(e), moduleName + "-DITAproc-GetAppleHelpImages")
                
        return dictCurDict
    
    def IterateNodes(self, xmldocument, attribname, targettype, linktypetocurrentfile, dictCurDict={}, strXPath = "//", pathtofile = ""):
        href = ""
        folder = os.path.dirname(pathtofile)
        xrefstructure = self.LinkFileStructure()
        ParentLinkInfo = self.LinkFileStructure()
        origTargetType = targettype
        ParentLinkInfo.strAbsPath = pathtofile
        ParentLinkInfo.strLinkedCurrentFileAs = linktypetocurrentfile
        ParentLinkInfo.strScope = "Unknown"
        
        #Create a function to store our xpath:
        xpatherator = etree.XPath(strXPath)
        matchedresults = xpatherator(xmldocument)
        
        for c in matchedresults:
            href = c.attrib[attribname]
            #if the first character is # then we have this is an internal xref and we don't need to process it further.
            if href.startswith("#"):
                continue
            href = href.split("#")[0]
            #Build out an absolute URL by combining the current folder path and the href (note: may contain ../)
            href = os.path.join(folder, href)
            ##Check the node to see if it has a "format" attribute specified.
            #if c.attrib.has_key("format"):
                #formatattribval = c.attrib["format"]
            if c.attrib.has_key("format"):
                targettype = c.attrib["format"]
            
            #' If the format specified in the attribute @format is "html" or "pdf", then we should check for external/internal scope.
            #' Additionally, sometimes URLs don't have this attribute set for some reason.  We should also check for the following:
            #' "http://" or "https://" or "mailto://" or "ftp://"            
            if targettype == "html" or targettype == "pdf" or string.find(href, "http://") > -1 or string.find(href, "https://") > -1 or string.find(href, "ftp://") > -1 or string.find(href, "mailto:") > -1:
                #' Check and then let the user know if they've somehow dropped their format="html" attribute from their xref...  Just an FYI.
                #' not having this attribute doesn't break the build, but it does mean something is different than our default template.
                if not c.attrib.has_key("format"):
                    msghandler.errorsObj.PrintMessage(2, "Missing @format='html' in xref. Containing file: " + pathtofile + ", Node: " + etree.tostring(c), moduleName + "-DITAproc-IterateNodes")

                #Get the scope of the ref and store it:
                if c.attrib.has_key("scope"):
                    xrefstructure.strScope = c.attrib["scope"]
                else:
                    xrefstructure.strScope = "local"
                
                xrefstructure.strAbsPath = href
                xrefstructure.strLinkedCurrentFileAs = targettype
                #Add them to the XrefHash and move on.
                #(If we're currently assigned to add content to the "externalxrefhash" (dictCurDict = extxrefhash) then we need to know to add it there rather than updating it directly...)
                if not self.ResultsDicts.dictExternalXrefHash.has_key(href):                
                    if self.ResultsDicts.dictExternalXrefHash == dictCurDict and not dictCurDict.has_key(href):
                        dictCurDict[href] = xrefstructure
                    else:
                        self.ResultsDicts.dictExternalXrefHash[href] = xrefstructure
            else: #This is an image, dita, or ditamap file.
                #Build out an absolute URL by combining the current folder path and the href:
                href = os.path.join(folder, href)
                #TODO: Do a check for capital letters for WebWorks Help here (make it depend on the output type = "wwh")
                # Check the  file for capital letters in the extension
                (shortname, extension) = os.path.splitext(href)
                if commonfuncs.hasCap(extension):
                    msghandler.errorsObj.PrintMessage(3, "Capital letter used in file extension. Some builds will fail. File: " + href, moduleName + "-DITAProc-IterateNodes")
                
                #Check to see if the linked file already exists in the currently selected hash table before adding it
                if not dictCurDict.has_key(href):
                    dictCurDict[href] = clsDITATopicInfo.DITATopicInfo(href, folder)
                    #msghandler.errorsObj.PrintMessage(1, "Adding: " + href, moduleName + "-DITAProc-IterateNodes")
                #try:
                if not os.path.exists(os.path.normpath(href)):
                    msghandler.errorsObj.PrintMessage(3, pathtofile + " references a non-existing file: " + href, moduleName + "-DITAproc-IterateNodes")
                #except Exception, e:
                    # store the message in our error obj:
                    #msghandler.errorsObj.PrintMessage(3, "Unpredicted error #1 while processing: " + href + ". Message: " + str(e), moduleName + "-DITAproc-IterateNodes")
                    
        
                    
                    
                #track topicrefs and xrefs separately here (to see if all xrefs to files are also topic ref'ed):
                if origTargetType == "xref" and not self.ResultsDicts.dictInternalXrefHash.has_key(os.path.normpath(href)):
                    self.ResultsDicts.dictInternalXrefHash[os.path.normpath(href)] = ParentLinkInfo
                elif origTargetType == "topicref" and not self.ResultsDicts.dictTopicRefHash.has_key(os.path.normpath(href)):
                    self.ResultsDicts.dictTopicRefHash[os.path.normpath(href)] = ParentLinkInfo
                
                # If we have a map or topic reference, then recurse through the submap/topic.
                if not (targettype == "image" or targettype == "html" or targettype =="pdf" or origTargetType == "xref"):
                    #try:
                    if os.path.exists(os.path.normpath(href)) and not os.path.normpath(href) == os.path.normpath(pathtofile):
                        self.parseFile(href, linktypetocurrentfile)
                    else:
                        msghandler.errorsObj.PrintMessage(2, pathtofile + " references a non-existing file or contains a circular reference to " + href, moduleName + "-DITAproc-IterateNodes")
                    #except Exception, e:
                       #msghandler.errorsObj.PrintMessage(3, "Unpredicted Error #2: " + str(e) + " File: " + href, moduleName + "-DITAproc-IterateNodes")
                elif targettype == "image" or targettype == "html" or targettype == "pdf":
                    #check to see if local images, pdfs, html files exist and throw an error message if they don't.
                    #try:
                    if not os.path.exists(os.path.normpath(href)):
                        msghandler.errorsObj.PrintMessage(3, pathtofile + " references a non-existing file: " + href, moduleName + "-DITAproc-IterateNodes")
                    #except Exception, e:
                        #msghandler.errorsObj.PrintMessage(3, "Unpredicted error #3: " + str(e) + " File: " + href, moduleName + "-DITAproc-IterateNodes")
        
        return dictCurDict #at the end, let's return the result of our findings so they can be added to the original.  
        #This is because we couldn't pass the dictionary by reference.

    def parseDir(self, pathtodir):
        pass
    
    def parseFile(self,pathtofile=__mypathtoxml__, LinkTypeToCurFile=""):
        #init our default tests:
        strEncoding = None
        blnFileisvalid = False
        #attempt to retrieve encoding from the current file.
        curfile = open(pathtofile, "r")
        strEncoding = findenc.detectXMLEncoding(curfile)
        curfile.close()
        curfile = None
        #msghandler.errorsObj.PrintMessage(0, "Encoding is set to %s on file %s." % (strEncoding,pathtofile), moduleName + "-parseFile")
        #if we found an encoding, let's see if the file is valid:
        if strEncoding != None:
            blnFileisvalid = self.FileIsValid(pathtofile)
        #now that we have our encoding and our validity testing done, let's crack open the DITA file and find all our possible linked files:
        if strEncoding != None:
            #open the file as an XML doc and start parsing using xpath searches
            myparser = etree.XMLParser(dtd_validation = False,resolve_entities=False)
            #try:
            try:
                doc = etree.parse(os.path.normpath(pathtofile),parser=myparser)
            except Exception, e:
                msghandler.errorsObj.PrintMessage(3, "Failed while trying to load content as XML file. Message: " + str(e) + " File: " + os.path.normpath(pathtofile), moduleName + "-parseFile")
                return False
                

        
            #try:
            # Create a new DITATopic object, this object stores information about each file
            # including details about its location, whether it is read-only,
            # error messages
            temptopic = clsDITATopicInfo.DITATopicInfo(pathtofile, os.path.dirname(pathtofile))
            #iterate image nodes in AppleHelp meta (will only happen if there is any to begin with so why not give it a shot)
            self.ResultsDicts.dictImageHash = self.GetAppleHelpImages(doc, self.ResultsDicts.dictImageHash, "//topicmeta/othermeta[contains(@name, 'LandingPageIcon')]/@content|//topicmeta/othermeta[contains(@name, 'AppleIcon')]/@content", pathtofile)
            #iterate image nodes in current topic
            self.ResultsDicts.dictImageHash = self.IterateNodes(doc, "href", "image", LinkTypeToCurFile, self.ResultsDicts.dictImageHash, "//image", pathtofile)
            #iterate topicref nodes in current map, recurse if found
            self.ResultsDicts.dictFileHash = self.IterateNodes(doc, "href", "topicref", LinkTypeToCurFile, self.ResultsDicts.dictFileHash, "//topicref", pathtofile)
            #' iterate xrefs to topics in current topic, recurse if found and local 
            #'only perform if linked-to file is not from a conref
            self.ResultsDicts.dictFileHash = self.IterateNodes(doc, "href", "xref", LinkTypeToCurFile, self.ResultsDicts.dictFileHash, "//xref[contains(@format, 'dita')]|//xref[not(@format)]", pathtofile)
            #iterate conref nodes in current topic, recurse if found
            self.ResultsDicts.dictConrefHash = self.IterateNodes(doc, "conref", "conref", LinkTypeToCurFile, self.ResultsDicts.dictConrefHash, "//*[@conref]", pathtofile)
            #iterate xref nodes in current topic, recurse if found
            self.ResultsDicts.dictExternalXrefHash = self.IterateNodes(doc, "href", "html", LinkTypeToCurFile, self.ResultsDicts.dictExternalXrefHash, "//xref[contains(@format, 'html')]|//xref[contains(@format, 'pdf')]", pathtofile)
            #except Exception, e:
                #msghandler.errorsObj.PrintMessage(3, "Unpredicted Error #0: " + str(e) + " MainFile: " + pathtofile, moduleName + "-DITAproc-parseFile")
    
            # Add current file to the collective hash
            if not self.ResultsDicts.dictFileHash.has_key(pathtofile):
                self.ResultsDicts.dictFileHash[pathtofile] = temptopic
            #except Exception, e:
                # store the message in our error obj:
                #msghandler.errorsObj.PrintMessage(3, "Unpredicted error while processing: " + pathtofile + ". Message: " + str(e), moduleName + "-DITAproc-parseFile")
        
    def start(self):
        msghandler.errorsObj.FlushMessages()
        pass
    
if __name__ == "__main__":
    __testcase__ = processEngineClass()
    results = __testcase__.start()
    print results
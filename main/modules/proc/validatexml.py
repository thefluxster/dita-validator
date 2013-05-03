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

from modules.common import msghandler
from modules.proc import ditaproc

moduleName = "ValidateXML"

class clsValidateXML(ditaproc.processEngineClass):
    
    def __init__(self, mainmappath="", catalogpath=os.path.join("dtds","catalog-dita.xml")):
        if mainmappath == "":
            msghandler.errorsObj.PrintMessage(3, "No path to a ditamap was passed when creating validation object.", moduleName)
            pass
        self.pathtocatalog = catalogpath
        self.__mypathtoxml__ = mainmappath  
        
    def parseDir(self, pathtodir):        
        #get list of files to be validated under the current folder (.xml and .ditamap)        
        #Actually, this list can be HUGE so forget about storing it for now. just loop through all the files checking if they're valid.
        self.ValidateFilesinDir(pathtodir)        
        
        
    def ValidateFilesinDir(self, pathtodir):        
        #loop through the files, validating each and reporting any issues.        
        #use os.walk to get info about current dir (pathtodir). Stores path to curdir (root), dirs, and files).
        for root, dirs, files in os.walk(pathtodir):
            for onefile in files:
                #don't want to do anything with the result, but we could (returns True or False)
                extension = string.lower(os.path.splitext(onefile)[1])
                if extension == ".xml" or extension == ".ditamap":
                    self.FileIsValid(os.path.join(root, onefile))                    
            for mydir in dirs:
            #loop into subdirs.
                self.ValidateFilesinDir(mydir)       
    
    def _ReplaceConref(self, ndeConrefSource1, strSourceFilepath):
        workingdir = os.path.dirname(strSourceFilepath)
        curfilename = os.path.basename(strSourceFilepath)
        #assume we only come here as a conrefnode. Just replace the children with the target content.  Don't recurse.
        assert isinstance(ndeConrefSource1, etree._Element)
        #Check to see if the current node has a conref attribute
        myattributes = ndeConrefSource1.attrib
        conrefval = ""
        if myattributes.has_key("conref"):
                conrefval = myattributes["conref"]
        if len(conrefval) > 0:
                relpath, anchor = string.split(conrefval, "#")
                if len(relpath) == 0:
                    #doesn't contain a filename, assume current file is the target.
                    relpath = curfilename
                targetpath = os.path.join(workingdir, relpath)
                #make sure the path exists:
                if not os.path.exists(os.path.normpath(targetpath)) or not os.path.isfile(targetpath):
                    #couldn't find target, return the path instead of the node.
                    return os.path.normpath(targetpath)
                #open the doc.
                myparser = etree.XMLParser(dtd_validation = False,resolve_entities=False)
                try:
                    targetdoc = etree.parse(targetpath, parser=myparser)
                except Exception, e:
                    msghandler.errorsObj.PrintMessage(3, "Failed while trying to load content as XML file. Message: " + str(e) + " File: " + os.path.normpath(targetpath), moduleName + "-ReplaceConref")
                    return False
                #strip the filename from the path now that we've got the doc open
                targetpath = os.path.dirname(targetpath)
                assert isinstance(targetdoc, etree._ElementTree)
                #find the node we referenced in the doc.
                if string.find(anchor, "/") > -1:
                    first, anchor = string.split(anchor, "/")
                targetnode = targetdoc.xpath("//*[contains(@id,'%s')]" % (anchor)) #this will return of list of one node at position 0.
                targetnode = targetnode[0] #xpath is the only way to use contains(), but we need this node isolated, not in a list.
                assert isinstance(targetnode, etree._Element)                        
                
                #clean out current node's potentially invalid sub content.        
                curchildren = ndeConrefSource1.xpath("* | processing-instruction() | text() | comment()")
                ndeConrefSource1.text = ""
                ndeConrefSource1.tail = ""
                for curchild in curchildren:
                        try:
                                curchild.clear()
                                if len(curchild) == 0:
                                        #Empty element, drop it
                                        ndeConrefSource1.remove(curchild)
                        except:
                                curchild = ""                                
                        

                #pull in the targetnode's content
                targetchildren = targetnode.xpath("node()")
                ndeConrefSource1.text = targetnode.text
                ndeConrefSource1.tail = targetnode.tail
                for targetchild in targetchildren:
                        if type(targetchild) == type(str()) or type(ndeConrefSource1) == type(unicode()):                                
                                ndeConrefSource1.tail = targetchild.tail
                        elif type(targetchild) == etree._Element:
                                ndeConrefSource1.append(targetchild)
                        elif type(targetchild) == etree._ProcessingInstruction:
                                ndeConrefSource1.append(targetchild)
                        elif type(targetchild) == etree._Comment:
                                ndeConrefSource1.append(targetchild)
        return ndeConrefSource1

    def _ReplaceConrefs(self, ndeConrefSource, strSourceFilepath):
            workingdir = os.path.dirname(strSourceFilepath)
            targetdir = workingdir #just in case there is no conref here...
            #assume we only come here form a conref node. Just replace the children and then check to see if those have more conrefs.
            assert isinstance(ndeConrefSource, etree._Element)
            #get the value of the conref attribute.
            myattributes = ndeConrefSource.attrib                        
            conrefval = ""
            if myattributes.has_key("conref"):
                    conrefval = myattributes["conref"]
            if len(conrefval) > 0:
                    #store the target path, so we can tell where new potential conrefs are supposed to jump from...
                    relpath, anchor = string.split(conrefval, "#")
                    targetpath = os.path.join(workingdir, relpath)
                    targetdir = os.path.dirname(targetpath)
            #Replace the children of the current node with the children of the target node 
            ndeConrefSource = self._ReplaceConref(ndeConrefSource, strSourceFilepath)
            if type(ndeConrefSource) == type(str()) or type(ndeConrefSource) == type(unicode()):
                #Failed to get a target conref file and the return result is not a node but rather a path to the missing file.
                msghandler.errorsObj.PrintMessage(3, "Conref'd file not found. Source: %s Target: %s." % (strSourceFilepath, ndeConrefSource), moduleName + "-ReplaceConrefs")
                return False
    
            #Get the new workingdir of the new children
            workingdir = targetdir
            #for each child, ReplaceConrefs if it has a conref attrib.        
            curchildren = ndeConrefSource.iterdescendants()
            for curchild in curchildren:
                    #if the target child contains a conref, we need to recurse into it (jumping from the new working dir).
                    tarattribs = curchild.attrib                        
                    targetpath2 = ""                    
                    if len(tarattribs) > 0:
                            conrefval = ""
                            if tarattribs.has_key("conref"):
                                    conrefval = tarattribs["conref"]
                            if len(conrefval) > 0:
                                    relpath, anchor = string.split(conrefval, "#")
                                    targetpath2 = os.path.join(workingdir, relpath)
                                    #targetdir = os.path.dirname(targetpath)
                    if len(targetpath2)>0:
                            #the whole thing needs replaced.
                            curchild = self._ReplaceConrefs(curchild, os.path.normpath(targetpath)) #we use targetpath here from above, not the new one. This gives us the path to the current node, not the newly discovered conref.
                            if curchild == False:
                                return False
                            #curchildindex = ndeConrefSource.index(curchild)
                            #ndeConrefSource.remove(curchild)
                            #ndeConrefSource.insert(curchildindex, newchild)
            return ndeConrefSource
            
    
    def _ResolveAllConrefs(self, filepath):
            curpath = os.path.dirname(filepath)
            myparser = etree.XMLParser(dtd_validation = False,resolve_entities=False)
            try:
                tree = etree.parse(filepath, parser=myparser)
            except Exception, e:
                msghandler.errorsObj.PrintMessage(3, "Failed while trying to load content as XML file. Message: " + str(e) + " File: " + os.path.normpath(filepath), moduleName + "-ResolveAllConrefs")
                return False
            #tell wing the object type we expect
            assert isinstance(tree, etree._ElementTree)
            #for each node with a conref in it, let's replace the placeholder content (recursively if necessary)
            for mynode in tree.findall("//*[@conref]"):
                    mynode = self._ReplaceConrefs(mynode, filepath)
                    if mynode == False:
                        return False
                    #print etree.tostring(mynode)
            return StringIO.StringIO(etree.tostring(tree))
    
    def getDTDforXML(self,pathtoxml):
        try:
            #open the xml file using minidom, read the public ID to a variable
            myparser = etree.XMLParser(dtd_validation = False,resolve_entities=False)            
            try:
                doc = etree.parse(pathtoxml, parser=myparser)
            except Exception, e:
                msghandler.errorsObj.PrintMessage(3, "Failed while trying to load content as XML file. Message: " + str(e) + " File: " + os.path.normpath(pathtoxml), moduleName + "-findDTDforXML")
                return False
            assert isinstance(doc, etree._ElementTree)
            
            mydocinfo = etree.DocInfo(doc)
            mypubid = mydocinfo.public_id
  
            #open the catalog-dita.xml file, find a matching reference            
            datasource = open(self.pathtocatalog)
            mycatalog = minidom.parse(datasource)
            datasource.close()
            datasource = None
            dtduris = mycatalog.getElementsByTagName("public")    
            for uri in dtduris:
                if uri.getAttribute("publicId") == mypubid:
                    pathtodtd = os.path.join(os.path.dirname(self.pathtocatalog), uri.getAttribute("uri"))
                    #return the path to the DTD to be used in the validation.
                    return os.path.normpath(pathtodtd)
            #If we came to this point, we failed to find a path to our DTD based on the pubid in the xml file
            msghandler.errorsObj.PrintMessage(2, "PublicId not recognized in catalog. PubID: " + mypubid, moduleName + "-findDTDforXML")
            return False
        except Exception, e:                           
            msghandler.errorsObj.PrintMessage(2, "Failed while trying to discover PublicID in XML file: " + os.path.normpath(pathtoxml), moduleName + "-findDTDforXML")
            return False
        
    
    def FileIsValid(self,pathtofile):
        dtdpath=self.getDTDforXML(pathtofile)
        dtd = ""
        if dtdpath == False:
            msghandler.errorsObj.PrintMessage(2, "Failed retrieving path to DTD. Cannot validate file: " + pathtofile, moduleName + "-validateFile")
            return False
        else:
            #msghandler.errorsObj.PrintMessage(0, "DTD used for validation: " + dtdpath, moduleName + "-validateFile")
            pass
        
        

        #########BEGIN Company CMS Specific Code - Not needed for normal validation#########
        #########Normally, just make sure all conrefs resolve properly on a filesystem#########
        #check to see if we have a CMS file
        sIODoc = False
        if pathtofile.find("GUID")==-1 and pathtofile.find("=v") == -1:
            #not a CMS doc, so all conrefs should resolve.
            #For each conref element, pull the target innerxml in as the current object to replace the node's innerxml.
            sIODoc = self._ResolveAllConrefs(pathtofile) #creates a StringIO returnstring (XML) that can can be parsed as XML.

        #########END Company CMS Specific Code#########
        
        
        
        if sIODoc == False:
            #msghandler.errorsObj.PrintMessage(2, "Unable to resolve all conrefs in file. Continuing as-is. Please correct links and retry validation. File: " + pathtofile, moduleName + "-validateFile")
            #just use the path to the file instead and then check validation as-is:
            sIODoc = pathtofile
        #Now that we've rebuilt the content, let's pass our modified version into the parser.
        myparser = etree.XMLParser(dtd_validation = False,resolve_entities=False)
        try:        
            doc = etree.parse(sIODoc,parser=myparser)
        except Exception, e:
            msghandler.errorsObj.PrintMessage(3, "Failed while trying to load content as XML file. Message: " + str(e) + " File: " + os.path.normpath(sIODoc), moduleName + "-ReplaceConref")
            return False        
        

            
            
            
           
        try:
            dtd = etree.DTD(os.path.normpath(dtdpath))
            try:
                ret = dtd.validate(doc)                
            except Exception, e:
                msghandler.errorsObj.PrintMessage(3, "Unpredicted error while validating. Message: " + str(e), moduleName + "-DITAproc-GetAppleHelpImages")
                ret = 0
        except Exception, e:
            msghandler.errorsObj.PrintMessage(3, "Unable to validate file. Could not find specified DTD: " + dtdpath + ". File: " + pathtofile + " Message: " + str(e), moduleName + "-validateFile")
            ret = 0
        
        #report our findings and return:
        if ret != 1:
            if not dtd == "":
                strErrorMsg = dtd.error_log.filter_from_errors()[0]
                if string.find(strErrorMsg.message, "Syntax of value for attribute id") > -1:
                    #If errors in an ID are the only issue we found, let's just report it as a warning and move on.
                    msghandler.errorsObj.PrintMessage(1, "Document is mostly valid. File: " + pathtofile + " Reason: " + strErrorMsg.message, moduleName + "-validateFile")
                    del dtd
                    del doc
                    return True
                msghandler.errorsObj.PrintMessage(3, "Document is not valid. File: " + os.path.normpath(pathtofile) + " Reason: " + strErrorMsg.message, moduleName + "-validateFile")
                #free up our resources:
                del dtd
                del doc            
                return False
            else:
                msghandler.errorsObj.PrintMessage(3, "Document may not be valid due to issue with DTD declaration. File: " + os.path.normpath(pathtofile), moduleName + "-validateFile")
            
        else:
            #msghandler.errorsObj.PrintMessage(0, "Document is valid. File: " + os.path.normpath(pathtofile), moduleName + "-validateFile")                       
            #free up our resources:
            del dtd
            del doc            
            return True                
                
    def start(self, debuglevel = "2"):
        #reset our message container:
        msghandler.errorsObj.FlushMessages()
        #make sure we were pased a file and not a directory...
        if os.path.isfile(self.__mypathtoxml__):
            self.parseFile(self.__mypathtoxml__)
        #We were sent a path to a dir to validate. Completely different logic and only applies to validation.  No link checking.
        elif os.path.isdir(self.__mypathtoxml__):
            self.parseDir(self.__mypathtoxml__)
        return msghandler.errorsObj.PrintLevelAndAboveMessagesToString(int(debuglevel))
    
if __name__ == "__main__":
    __testmappath__ = os.path.join(os.path.normpath(os.path.curdir), "samples")
    __testmappath__ = os.path.join(__testmappath__,"mainmap.ditamap")
    print "running testcase only..."
    __testcase__ = clsValidateXML(__testmappath__)
    print __testcase__.start()
    
    
    
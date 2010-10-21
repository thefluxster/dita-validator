#!/usr/bin/env python
import string

class errorHandlerClass():
    dictErrors = {}
    intErrors = 0
    exitcode = 0    
    class messageClass():
        """Class to track messages from calling programs. Severity can be any of the following:
        0 = Debugging
        1 = Info
        2 = Warning
        3 = Error
        4 = Fatal
        """
        severity = 0
        message = "default"
        reportingModule = ""
        
    def FlushMessages(self):
        self.dictErrors = {}
        
    def PrintMessage(self, intSeverity, strMessage, strCallingModule):
        oError = self.messageClass()
        #Build the error object to see if we have encountered it yet.        
        oError.severity=intSeverity
        oError.message=strMessage
        oError.reportingModule = strCallingModule
        #Check to see if we've encountered this error yet for any Errors and Warnings...
        previouserror = False
        
        if intSeverity >= 3:
            highseverity = True
        else:
            highseverity = False
        if highseverity == True:
            for tempoError in self.dictErrors.values():        
                if oError.message == tempoError.message:
                    previouserror = True
                    break
        if previouserror == False:
            self.intErrors += 1
            if intSeverity > 1:  #Use 0 for pass, 1 for any other types, 2 for syntax errors on command line.
                self.exitcode = 1            
            self.dictErrors[self.intErrors] = oError

    def PrintMessagesToString(self, intSeverity):
        dictCurErrors = self.dictErrors
        strMessages = "\n"
        severityLevel = "DEBUGGING"
        for key in dictCurErrors:
            value = dictCurErrors[key]
            if value.severity == 0:
                severityLevel = "DEBUGGING"
            elif value.severity == 1:
                severityLevel = "INFO"            
            elif value.severity == 2:
                severityLevel = "WARNING"
            elif value.severity == 3:
                severityLevel = "ERROR"
            elif value.severity == 4:
                severityLevel = "FATAL"
            strMessages =  strMessages + "[%s] %s: %s\n" % (dictCurErrors[key].reportingModule,severityLevel,dictCurErrors[key].message)
        
        return strMessages 
        
    def PrintLevelAndAboveMessagesToString(self, intSeverity):
        dictCurErrors = self.dictErrors
        strMessages = "\n"
        severityLevel = "DEBUGGING"
        for key in dictCurErrors:
            value = dictCurErrors[key]
            if value.severity == 0:
                severityLevel = "DEBUGGING"
            elif value.severity == 1:
                severityLevel = "INFO"            
            elif value.severity == 2:
                severityLevel = "WARNING"
            elif value.severity == 3:
                severityLevel = "ERROR"
            elif value.severity == 4:
                severityLevel = "FATAL"
            if intSeverity <= value.severity:
                strMessages =  strMessages + "[%s] %s: %s\n" % (dictCurErrors[key].reportingModule,severityLevel,dictCurErrors[key].message)
        
        return strMessages             

errorsObj = errorHandlerClass()
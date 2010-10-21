#!/usr/bin/env python

import time
import datetime

# String processing:
def hasCap(s):
    """returns True if the string s contains a capital letter"""
    for num in range(65, 91): # A to Z
        capLetter = chr(num)
        if capLetter in s:
            return True
    return False

def GetTextTimeStamp():
    return str(datetime.datetime.now())



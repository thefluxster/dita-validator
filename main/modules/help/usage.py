import sys
def usage():
    print """
    Usage: DITAValidator [-map ditamap] [-c catalog] [-o outputdir]
    --map ditamap             Pass a full path to the master map
    --catalog catalog         Path to the catalog to be used for validating the XML
    
    Optional parameters:
    --debug {debuglvl}        Turns on debugging mode
                              With no parameter, only 'FATAL' messages are reported.")
                              Other parameters:")
                              1 = 'DEBUG' or higher.")
                              2 = 'WARNING' or higher.")
                              3 = 'ERROR' or higher.")
                              4 = 'FATAL' only.")
    --encoding encoding       Pass through the encoding such as UTF-8 or UTF-16.
                              Default behavior is to convert to UTF-16.
    --indexsortas             Inserts the index-sort-as
    --acceptchanges           Accepts all pending tracked changes.
    --remnestedchanges        Removes nested track changes.
    --outputdir outputdir     Copies files before processing. Results stored in 'file_manifest.log'.
    --properties              Creates a properties file that contains DITA info.
    --rmwhitespace            Cleans out the whitespace.  Not turned on by default       
    """
    
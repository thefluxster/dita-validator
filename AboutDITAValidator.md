# Introduction #

The DITA Validator is a Python utility designed to quickly and efficiently validate all the content linked from a main ditamap. It also has the ability to quickly validate Trisoft XML where links do not resolve but content is stored in one location.

# Details #

I haven’t ported all of the .NET functionality for cleaning up issues in the XML or prepping content for sending to localization (hooks are there, but it hasn’t been coded). I have, however, ported the basic link checks and added the required pieces for validation checking.  I also made it possible to just toss it a directory and do just the validation checking on content in that directory. Files being validated/parsed must have an .xml, .dita, or .ditamap extension. DTDs are specified by pointing to your catalog file before running the validation.
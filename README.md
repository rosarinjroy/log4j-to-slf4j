Introduction
===
This is utility that can be used to convert Log4j formatted log statements to SLF4J formatted log statements.

A sample input is:
    logger.info("Hello " + who);

Will be converted to:
    logger.info("Hello {}", who);
    
Pre-requisites
===
You should have Python 2.7.x should be installed.

It is assumed that you are using SLF4J 1.7 or later that has varadic argument support.

How to run?
===
It is very easy to run this script. Just invoke the script with the file names as arguments.
    log4jtoslf4j.py ExampleInput.java

The original input file will be saved with a .orig extension. You can provide multiple input files as arguments.

Important notes
===
# It is assumed that your loggers are named as log or logger (case insensitive). If you have named your logger in any other way, 
please modify the global variable LOGGER_NAMES and get it work.
# There are cases when the converter cannot reliably convert the arguments. In such cases, it will print a warning
message and leave the old arguments as it is. In such cases you should fix them.

Licensed under BSD license. Read the LICENSE file.

Enjoy!
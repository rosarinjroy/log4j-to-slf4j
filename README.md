Introduction
===
This is a simple utility that can be used to convert Log4j formatted log statements to SLF4J formatted log statements.

A sample input is:

    logger.info("Hello " + who);

Will be converted to:

    logger.info("Hello {}", who);

Pre-requisites
===
You should have Python 2.7.x installed.

It is assumed that you are using SLF4J 1.7 or later that has varadic argument support.

How to run?
===
It is very easy to run this script. Just invoke the script with the file names as arguments.

    log4jtoslf4j.py ExampleInput.java

The original input file will be saved with a .orig extension. You can provide multiple input files as arguments.

Important notes
===
* It is assumed that your loggers are named as log or logger (case insensitive). If you have named your logger in any other way, please modify the global variable LOGGER_NAMES and it should work.
* It is recommended that you run the converter only on files that have already been checked-in. Otherwise, if something goes wrong, you might lose your partial work (and you cannot blame me for that ;-)
* There are cases when the converter cannot reliably convert the arguments. In such cases, it will print a warning
message and leave the old arguments as it is. In such cases you should manually fix them.
* Please watch out for WARN messages while the script is running. If there are any WARN messages, you may have to convert those log strings yourself.
* If you would like to run this script on a directory, you can simply use the find command as below:

    log4jtoslf4j.py `` `find . -type f -name '*.java'` ``

Testing
===
It is strongly recommended that you take a look at ExampleInput.java.input file to understand what kind of inputs can be processed. To run the converter locally, you can simply run the test.sh file. This will run the converter and tell you if the conversion was successful.

    ./test.sh

Licensed under BSD license. Read the LICENSE file.

Enjoy!

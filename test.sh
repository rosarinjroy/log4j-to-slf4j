#!/bin/bash
echo "Running tests ..."

echo "Copying the input file ..."
cp ExampleInput.java.input ExampleInput.java

echo "Runing the converter ..."
python log4jtoslf4j.py ExampleInput.java

echo "Verifying the output ..."
diff ExampleInput.java ExampleInput.java.output

if [[ "$?" -eq "0" ]] ; then
    echo "TESTS PASSED."
else
    echo "*** FATAL *** TESTS FAILED."
    echo "You can compare the actual output with expected output (ExampleInput.java.output)."
    echo "If you think something is wrong, please file a bug report."
fi


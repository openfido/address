#!/bin/bash
#
# Generic python environment for OpenFIDO
#
TESTED=0
FAILED=0
FILES=
for OPENFIDO_INPUT in $(find $PWD/autotest -name 'input_*' -print); do
    echo "Processing $OPENFIDO_INPUT..."
    export OPENFIDO_INPUT
    export OPENFIDO_OUTPUT=${OPENFIDO_INPUT/autotest\/input_/autotest\/output_}
    mkdir -p $OPENFIDO_OUTPUT
    rm -rf $OPENFIDO_OUTPUT/{*,.??*}
    if ! python3 openfido.py 1>$OPENFIDO_OUTPUT/openfido.out 2>$OPENFIDO_OUTPUT/openfido.err; then
        FAILED=$(($FAILED+1)) 
        FILES="$FILES ${OPENFIDO_INPUT/$PWD\//}"
        echo "ERROR: $OPENFIDO_INPUT test failed"
    fi
    TESTED=$(($TESTED+1))
done

echo "Tests completed"
echo "$TESTED tests completed"
echo "$FAILED tests failed"
if $FAILED -gt 0; then
    tar cfz validate-result.tar.gz $FILES
fi
time
exit $FAILED

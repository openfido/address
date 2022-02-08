#!/bin/bash
#
# Generic python environment for OpenFIDO
#
set -x

TESTED=0
FAILED=0
for OPENFIDO_INPUT in $(find $PWD/autotest -name 'input_*' -print); do
    echo "Processing $OPENFIDO_INPUT..."
    export OPENFIDO_INPUT
    export OPENFIDO_OUTPUT=${OPENFIDO_INPUT/autotest\/input_/autotest\/output_}
    mkdir -p $OPENFIDO_OUTPUT
    rm -rf $OPENFIDO_OUTPUT/{*,.??*}
    if ! python3 openfido.py 1>$OPENFIDO_OUTPUT/openfido.out 2>$OPENFIDO_OUTPUT/openfido.err; then
        set FAILED=$(($FAILED+1)) 
        echo "ERROR: $OPENFIDO_INPUT test failed"
    fi
    TESTED=$(($TESTED+1))
done

echo "Tests completed"
echo "$TESTED tests completed"
echo "$FAILED tests failed"
time
exit $FAILED

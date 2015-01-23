#!/bin/bash

# This script runs the tests in Python 2.7, Python 3.4, and PyPy
# a virtualenv for each of these, repectively, should be avaiable at
# venv, venv3, and venvpypy
if [[ "$VIRTUAL_ENV" != "" ]]
then
    deactivate
fi

EXITCODE=0

venv/bin/nosetests
PYTHON2_EXITCODE=$?
venv3/bin/nosetests
PYTHON3_EXITCODE=$?
venvpypy/bin/nosetests
PYPY_EXITCODE=$?

if [[ $PYTHON2_EXITCODE != 0 ]]
then
    echo 'python 2.7 tests failed'
    EXITCODE=$PYTHON2_EXITCODE
fi
if [[ $PYTHON3_EXITCODE != 0 ]]
then
    echo 'python 3.4 tests failed'
    EXITCODE=$PYTHON3_EXITCODE
fi
if [[ $PYPY_EXITCODE != 0 ]]
then
    echo 'pypy tests failed'
    EXITCODE=$PYPY_EXITCODE
fi
exit $EXITCODE

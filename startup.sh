#!/bin/bash
cmd_dir=`dirname $0`
cd $cmd_dir
export GOOGLE_APPLICATION_CREDENTIALS=`ls ../*json | head -1`
echo $GOOGLE_APPLICATION_CREDENTIALS
python ./example_recognizer.py

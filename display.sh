#!/bin/bash
# don't run if we're not attached to a terminal
if [[ ! -t 1 ]]; then
  exit 0
fi
OUTPUT="/tmp/piday.out"
if [[ ! -e "$OUTPUT" ]]; then
  echo "waiting for the recognizer to start up"
  while [[ ! -e "$OUTPUT" ]];
  do
    sleep 1
  done
fi
echo "$0 $$ displaying recognizer output"
echo "quit quit quit to exit"
tail -f /tmp/piday.out
exit 0

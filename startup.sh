#!/bin/bash
cmd_dir=`dirname $0`
cd $cmd_dir
export GOOGLE_APPLICATION_CREDENTIALS=`ls ../*json | head -1`
echo $GOOGLE_APPLICATION_CREDENTIALS
./showtext 'waiting for IP'
while :
do
  sleep 1
  ping -c 1 www.github.com 2>&1
  rc=$?
  if [[ $rc -eq 0 ]]; then
    break
  fi
done
MY_ADDRESS=$(ifconfig | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}')
echo "My address is $MY_ADDRESS"
./showtext "My address is $MY_ADDRESS"

python ./example_recognizer.py 2>/tmp/piday.err >/tmp/piday.out

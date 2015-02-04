#!/bin/sh

echo 'first decode:'
echo

./stattime_decode.py 1 |sort -n -k 9

echo
echo
echo

echo 'second decode:'
echo

./stattime_decode.py 2 |sort -n -k 9


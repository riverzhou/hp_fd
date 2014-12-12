#!/bin/sh

./statconn_image.py | sort -n -k 6

echo
echo
echo

./statconn_price.py | sort -n -k 6


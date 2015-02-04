#!/bin/sh

echo 'first image:'
echo

./statconn_image.py 1 | sort -n -k 6

echo
echo
echo

echo 'first price:'
echo

./statconn_price.py 1 | sort -n -k 6

echo
echo
echo

echo 'second image:'
echo

./statconn_image.py 2 | sort -n -k 6

echo
echo
echo

echo 'second price:'
echo

./statconn_price.py 2 | sort -n -k 6


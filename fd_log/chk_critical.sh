#!/bin/sh

wc -l log/*critical.log

grep '' log/*critical.log | grep -v '\[Errno 110\]'


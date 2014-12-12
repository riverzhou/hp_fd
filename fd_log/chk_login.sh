#!/bin/sh

grep 'login' log/*warning.log |grep -v 'failed'


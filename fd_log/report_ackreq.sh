#!/bin/sh

count=9

#---------------------------------------------------------------------

echo imagecode:

grep ' 11:29' log/*time.log| grep imagecode.aspx |wc -l
grep ' 11:29' log/*info.log| grep imagecode.aspx |wc -l

echo

echo bid:

grep ' 11:29' log/*time.log| grep bid.aspx |wc -l
grep ' 11:29' log/*info.log| grep bid.aspx |wc -l

echo
for i in $( seq 1 $count )
do
	echo imagecode ${i} :
	grep ' 11:29' log/0${i}_log_time.log| grep imagecode.aspx |wc -l
	grep ' 11:29' log/0${i}_log_info.log| grep imagecode.aspx |wc -l
done

echo
for i in $( seq 1 $count )
do
	echo bid ${i} :
	grep ' 11:29' log/0${i}_log_time.log| grep bid.aspx |wc -l
	grep ' 11:29' log/0${i}_log_info.log| grep bid.aspx |wc -l
done


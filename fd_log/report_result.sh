#!/bin/sh

#20       ['72600', '73600', None]
#18       ['72600', '73500', None]
#16       ['72600', '73500', '73700']
#11       ['72600', '73500', '73800']
#3        ['72600', None, None]
#1        [None, '73500', '73700']
#1        [None, '73500', '73800']
#1        [None, None, None]


a="'72600', '73600', None"
b="'72600', '73500', None"
c="'72600', '73500', '73700'"
d="'72600', '73500', '73800'"
e="'72600', None, None"
f="None, '73500', '73700'"
g="None, '73500', '73800'"
h="None, None, None"


echo
echo $a
grep -e "${a}" 5_result.txt
grep -e "${a}" 5_result.txt |wc -l

echo
echo $b
grep -e "${b}" 5_result.txt
grep -e "${b}" 5_result.txt |wc -l

echo
echo $c
grep -e "${c}" 5_result.txt
grep -e "${c}" 5_result.txt |wc -l

echo
echo $d
grep -e "${d}" 5_result.txt
grep -e "${d}" 5_result.txt |wc -l

echo
echo $e
grep -e "${e}" 5_result.txt
grep -e "${e}" 5_result.txt |wc -l

echo
echo $f
grep -e "${f}" 5_result.txt
grep -e "${f}" 5_result.txt |wc -l

echo
echo $g
grep -e "${g}" 5_result.txt
grep -e "${g}" 5_result.txt |wc -l

echo
echo $h
grep -e "${h}" 5_result.txt
grep -e "${h}" 5_result.txt |wc -l


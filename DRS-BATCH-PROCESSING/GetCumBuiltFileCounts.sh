#!/bin/bash 

export ME=$(basename $0)

inFile=${1?"${ME}:Input file required, not given"}

[ -f $inFile ] || { echo ${ME}:Input not found, or not file ; exit 1; }

awk  ' { cmd = "find  " $1 " -type f | wc -l"
cmd | getline thisCount
close(cmd)
sumCount += thisCount
print $1 "|" thisCount "|" sumCount }'  < $inFile 


#!/bin/bash

export ME=$(basename $0)

inFile=${1?"${ME}:Input file required, not given"}

[ -f $inFile ] || { echo ${ME}:Input not found, or not file ; exit 1; }

# in take 2 we're just looking in the directories, because the input 
# is now a directory itself
# while read gg ; do awk ' { cmd = "find $(dirname " $1 ") -type f | wc -l"
while read gg ; do awk  ' { cmd = "find  " $1 " -type f | wc -l"
cmd | getline thisCount
close(cmd)
sumCount += thisCount
print $1 "|" thisCount "|" sumCount }' ; done < $inFile 
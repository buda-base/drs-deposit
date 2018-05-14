#!/bin/bash
while read gg ; do awk ' { cmd = "find $(dirname " $1 ") -type f | wc -l"
cmd | getline thisCount
close(cmd)
sumCount += thisCount
print $1 "|" thisCount "|" sumCount }' ; done < DictUnDepositedBuildPaths.txt | sed 's:/batch.xml::'

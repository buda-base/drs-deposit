#!/bin/bash
#
# Searches for deposited volumes in the downloaded cumulatie dictionary (from WebAdmin - ! must have been downloaded with
# optional added column 'volume Directory'
#
# --------     Reads files: ---------------
# DICT (see below) - cumulative dictionary
# 
# BuildList:  	output of RemoveDuplicatevolumes.sh - this is the
# pool of volumes which is ready for deposit.
#
# -------------- Writes files -----------------
#
# DictFields: from dictionary, volume directories
#
# UnDepositedBuildPaths.txt: Set difference between curDeposits  
#
ME=$(basename $0)

buildList=${1?"${ME}:Build list argument required, not given"}
outFile=${2?"${ME}:Output file must be given."}

[ -f $buildList ] || { echo "${ME}:BuildList doesnt exist" ; exit 1 ; }


# Take 2: use the dictionary
export DICT=~/drs-deposit/output/BDRCCumulativeProdDeposits.csv

# You may ask: why not just look for a batch directory:
# Because the batch directories may have different roots, or a 
# volume may have been built in several batch directories.
#
# Heuristic. Here's a known volume build. find its column index
# in the dictionary
export PROBE=W00KG02536-I00KG03142
#
for idx in $(seq 1 25) ;
do
    test=$(awk -F',' -v fNum=$idx -v searchTarget=$PROBE '{ if ($fNum == searchTarget) {print fNum}}' $DICT)
    [ ! -z "$test" ] && break 
done
result=$(printf "Found volume %s in comma separated field %s\n" $PROBE $idx)
echo $result
#
# Could use grep, bu I want the field separation syntax to be the same,
# sometimes there are commas in quoted fields
awk -F',' -v volumeField=$idx '{print $volumeField }' $DICT | sort -u > DictFields

# This line only removed the specific lines. It leaves in batches where the line appeared.
# grep -w -v -f DictFields  $buildList | sort -u > $outFile
# Change so that it gets all the batch directories which contain one or volumes which are in dict.
 grep -w -f DictFields volList.txt | xargs -n 1 dirname | sort -u | xargs -n1 basename > batchesWithADeposit
 # Now scan volList to remove those batches
 grep -w -v -f batchesWithADeposit volList.txt > $outFile
 #


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

# YOu can try a heuristic. Here's a known volume build:
export PROBE=W00KG02536-I00KG03142
#
# Take 2: look for a volume OSN, and
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

#

grep -w -v -f DictFields  $buildList | sort -u > $outFile


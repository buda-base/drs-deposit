#!/bin/bash
#
# Searches for deposited volumes in two sources:
# - all downloaded loadreports
# - the downloaded cumulatie dictionary (from WebAdmin - ! must have been downloaded with
# optional added column 'volume Directory'
#
# --------     Reads files: ---------------
# DICT (see below) - cumulative dictionary
#
# BUILD_ROOT - parent of all LOADREPORT files
# 
# BuildList:  	output of RemoveDuplicatevolumes.sh - this is the pool of volumes
#				which is ready for deposit.
#
# -------------- Writes files -----------------
# 
# curDeposits: extracted from LOADREPORTW
#
# DictFields: from dictionary, volume directories
#
# UnDepositedBuildPaths.txt: Set difference between curDeposits  
#
# Take 2: use the dictionary
export DICT=~/drs-deposit/output/BDRCCumulativeProdDeposits.csv
#
# Can't always determine volume directory column position.
#
# Have to experiment
#  awk -F',' '{print $11}' ~/drs-deposit/output/BDRCCumulativeProdDeposits.csv | sort -u > curDeposits

# YOu can try a heuristic. Here's a known volume build:
export PROBE=batchW00CHZ0103335-1
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
# Given a list of deposited volumes (batchWxxxxxx-1)
# filter them out of a list of available built batches.
# See RemoveDuplicateBuilds for generating a unique list of builds, 
# to eliminate risk of duplicating future builds.
# in /Volumes/DRS_Staging/DRS/KhyungUploads/prod, look for any file named LOADREPORT
# theres 
#export BUILD_ROOT=/Volumes/DRS_Staging/DRS/KhyungUploads/prod
#find $BUILD_ROOT -type f -name \*LOADREPORT\* -exec basename {} \; | sed -e 's/LOADREPORT//' -e 's/_//' -e 's/\*//' -e 's/\.txt//' | sort | uniq > curDeposits
#
# Where BuildList.txt is created by RemoveDuplicateBuilds.sh
# grep -w -v -f curDeposits  BuildList.txt | sort -u > UnDepositedBuildPaths.txt
grep -w -v -f DictFields  BuildList.txt | sort -u > DictUnDepositedBuildPaths.txt




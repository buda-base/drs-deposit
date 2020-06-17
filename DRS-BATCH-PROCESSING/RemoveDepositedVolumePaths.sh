#!/usr/bin/env bash
#
# Searches for deposited volumes in the downloaded cumulative dictionary (from WebAdmin - ! must have been downloaded with
# optional added column 'volume Directory'
#
# --------     Reads files: ---------------
# DICT (see below) - cumulative dictionary
# 
# BuildList:  	output of RemoveDuplicateVolumes.sh - this is the
# pool of volumes which is ready for deposit.
#
# -------------- Writes files -----------------
#
# $dictFieldsFile: from dictionary, volume directories
#
# UnDepositedBuildPaths.txt: Set difference between curDeposits  
#
ME=$(basename "$0")

buildList=${1?"${ME}:Build list argument required, not given"}
outFile=${2?"${ME}:Output file must be given."}

[ -f "$buildList" ] || { echo "${ME}:BuildList doesnt exist" ; exit 1 ; }

[ -z "$BB_LEVEL" ] && {  echo "${ME}:error: BB_LEVEL not set. Source SetBBLevel.sh" ; exit 1 ; }

# Take 2: use the dictionary
export DICT=/Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCumulativeProdDeposits.csv
BATCHES_WITH_DEPOSIT=batchesWithADeposit

# You may ask: why not just look for a batch directory:
# Because the batch directories may have different roots, or a 
# volume may have been built in several batch directories.
#
# Heuristic. Here's a known volume build. find its column index
# in the dictionary
# This OSN is known to exist in both Prod and QA
export PROBE=W1GS66344-I1GS66346
#
for idx in $(seq 1 25) ;
do
    test=$(awk -F',' -v fNum="$idx" -v searchTarget=$PROBE '{ if ($fNum == searchTarget) {print fNum}}' $DICT)
    [[ -n "$test" ]] && break
done
result=$(printf "Found volume %s in comma separated field %s\n" $PROBE "$idx")
echo "$result"

dictFieldsFile=$(mktemp)
#
# Could use grep, bu I want the field separation syntax to be the same,
# sometimes there are commas in quoted fields
awk -F',' -v volumeField="$idx" '{print $volumeField }' $DICT | sort -u > "$dictFieldsFile"

# This line only removed the specific lines. It leaves in batches where the line appeared.
# grep -w -v -f $dictFieldsFile  $buildList | sort -u > $outFile
# Change so that it gets all the batch directories which contain one or volumes which are in dict.
 grep -w -f "$dictFieldsFile" "$buildList" | xargs -n 1 dirname | sort -u | xargs -n1 basename > $BATCHES_WITH_DEPOSIT
 # Now scan volList to remove those batchesR_WITH_DEPOSIT
# if there are no deposited batches, just copy the volume list
# (because gre -v -f empty file produces no output
if [[ ! -s $BATCHES_WITH_DEPOSIT ]]
then
  cp "$buildList" "$outFile"
else
  grep -w -v -f $BATCHES_WITH_DEPOSIT "$buildList" > "$outFile"
fi


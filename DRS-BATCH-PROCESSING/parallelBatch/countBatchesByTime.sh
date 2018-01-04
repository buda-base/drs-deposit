#!/bin/bash
# Synopsis: When running a number of 'make-drs-batch' instances in parallel, this script
# counts the number of completed batches, by counting the number of existing "batch.xml" files.
# It runs until explicitly killed.
# Best used in a background script which appends to a file.
#
# Dependencies: BIGHOME: the location of the batchbuilders' output (see makeOneDrs.sh)

BIGHOME=/Volumes/DRS_Staging/DRS/TestBigRuns
while true ; do 
   printf "%s\t%d\n" $(date +%H:%M) $(find $BIGHOME -name batch\.xml -maxdepth 3 | wc -l)
   sleep 120s
done

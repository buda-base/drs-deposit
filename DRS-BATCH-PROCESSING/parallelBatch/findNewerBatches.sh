#! /bin/bash -vx
#
# Synopsis: find batches newer than a certain number of minutes
#
# Arguments:
#   time: an integer representing the age threshold: batches older than this are not returned.
find /Volumes/DRS_Staging/DRS/TestBigRuns -name batch.xml -maxdepth 3 -Bmin -$1 -ls

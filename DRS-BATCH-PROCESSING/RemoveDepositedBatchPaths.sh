#!/bin/bash
#
# Given a list of deposited batches (batchWxxxxxx-1)
# filter them out of a list of available built batches.
# See RemoveDuplicateBuilds for generating a unique list of builds, 
# to eliminate risk of duplicating future builds.
# in /Volumes/DRS_Staging/DRS/KhyungUploads/prod, look for any file named LOADREPORT
# theres 
export BUILD_ROOT=/Volumes/DRS_Staging/DRS/KhyungUploads/prod
find $BUILD_ROOT -type f -name \*LOADREPORT\* -exec basename {} \; | sed -e 's/LOADREPORT//' -e 's/_//' -e 's/\*//' -e 's/\.txt//' | sort | uniq > curDeposits
#
# Where BuildList.txt is created by RemoveDuplicateBuilds.sh
grep -w -v -f curDeposits  BuildList.txt > UnDepositedBuildPaths.txt



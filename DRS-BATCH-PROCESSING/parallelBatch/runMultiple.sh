#!/bin/bash
#
# launch and track a bunch of background tasks
# 
# Arguments:
#	1:  beginning worksList number
#   2.  Ending worksList number
# Dependencies:
#
# splitWorks.sh: runMultiple expects that splitWorks has created 
# a directory named ${WORKS_SRC} which contains
# a list of files named ${WORKS_LIST_FN}nnnn.txt where nnnn is any
# arbitrary integer.
# 
# If there are gaps in the sequence, makeOneDrs.sh fails, no big deal.
#
# Some constants
#
# HACK: Magic number: makeOneDrs.sh depends on this
WORKS_LIST_FN=worksList
#
# Source of works
WORKS_SRC=bigRuns


underwayDir=timing/underway
[ -d  $underwayDir ] || mkdir -p $underwayDir
#
resultsDir=timing/finishedRuns
[ -d  $resultsDir ] || mkdir -p $resultsDir

for x in $(seq $1 $2 ); do
	#
	# do_real_work
	#
	# jsk 12.22.17 Put the iteration here where we can see it
	# Run each iteration in the background
    ./makeOneDrs.sh ${WORKS_SRC}/${WORKS_LIST_FN}${x}.txt $underwayDir $resultsDir &
 
done

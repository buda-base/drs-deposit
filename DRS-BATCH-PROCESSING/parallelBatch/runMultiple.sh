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
WORKS_SRC=runSources
# jsk Take 2 for parallel processing
# WORKS_SRC=smallRuns
# WORKS_SRC=issue34

function usage() {
	cat << USAGE
		synopsis: runMultiple wl1 wl2[=wl1]
		run multiple lists of works in files ${WORKS_SRC}/worksList\$wl1 ... \$wl2.txt
		wl2 defaults to wl1 if not given.
		wl2 can be less than wl1 - bash seq is the iterator
USAGE
}

underwayDir=timing/underway
[ -d  $underwayDir ] || mkdir -p $underwayDir
#
resultsDir=timing/finishedRuns
[ -d  $resultsDir ] || mkdir -p $resultsDir

# if no args, bail
[ x"$1" == "x" ] && { usage ; exit 1 ; }

wl1=$1
wl2=$2

[ x"$wl2" == "x" ] && { usage ; printf '\n** running one ** %s\n' $wl1 ; wl2=$wl1 ; }

for x in $(seq $wl1 $wl2 ); do
	#
	# do_real_work
	#
	# jsk 12.22.17 Put the iteration here where we can see it
	# Run each iteration in the background
	# jsk 21.I.18: shell scripts can be in ~/bin
        
	makeOneDrs.sh ${WORKS_SRC}/${WORKS_LIST_FN}${x}.txt $underwayDir $resultsDir &
 
done

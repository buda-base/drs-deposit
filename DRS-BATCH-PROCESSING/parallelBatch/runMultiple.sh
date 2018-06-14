#!/bin/bash
#
# launch and track a bunch of background tasks
# 
# Arguments:
#	List of files
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
# Dont export
ME=$(basename $0)
#

function usage() {
	cat << USAGE
		synopsis: $ME [-h] file1,file2,...
		-h: shows this message
		run multiple lists of works given in 'files'
		in parallel execution, One process per file

USAGE
}



while getopts h opt ; do
	# echo "in getopts" $opt $OPTARG
	case $opt in
		h)
			usage
			exit 0
			;;
	esac
done

underwayDir=timing/underway
[ -d  $underwayDir ] || mkdir -p $underwayDir
#
resultsDir=timing/finishedRuns
[ -d  $resultsDir ] || mkdir -p $resultsDir

# if no args, bail
[ x"$1" == "x" ] && { usage ; exit 1 ; }

for x in $* ; do
	#
	# do_real_work
	#
	# jsk 12.22.17 Put the iteration here where we can see it
	# Run each iteration in the background
	# jsk 21.I.18: shell scripts can be in ~/bin
        
	makeOneDrs.sh $x $underwayDir $resultsDir &
 
done

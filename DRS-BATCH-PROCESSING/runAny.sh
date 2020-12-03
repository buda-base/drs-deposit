#!/usr/bin/env bash
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
		synopsis: $ME [-h] func <args>
		-h: shows this message
		run the process 'func' in a parallel subhsell. 
		against each of the args in <args>

USAGE
}

while getopts h opt ; do
	# echo "in getopts" $opt $OPTARG
	case $opt in
		h)
			usage
			exit 0
			;;
		*)
		    usage
		    exit 1
		    ..
	esac
done

func=${1?$(usage)}
shift

# Sigh. We need to do this because we're not in our login shell
# Specific to  debian
# [[ -f /usr/bin/env_parallel.bash ]] && { . /usr/bin/env_parallel.bash ;  }

# env_parallel --record-env

set -v
set -x
parallel   --joblog="drs.$(date +%H-%M-%S).para.log" \
           --results runout-$(date +%H-%M-%S) \
	     $func {}  ::: $*

# for x in $* ; do
# 	#
# 	# do_real_work
# 	#
# 	# jsk 12.22.17 Put the iteration here where we can see it
# 	# Run each iteration in the background
# 	# jsk 21.I.18: shell scripts can be in ~/bin
        
# 	echo ${func} $x $underwayDir $resultsDir &
 
# done

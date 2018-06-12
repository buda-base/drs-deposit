#! /bin/bash
#   Make one DRS Launch, with tracking control
#
# arguments:

#
function Usage {
cat << ENDUSAGE
synopsis:
	makeOneDrs  workListFileName statusRoot completionRoot

	worksListFileName: 	Path to a file containing lines of
						comma separated Work,HOLLIS tuples.
						HACK ALERT: filename must have the format
						worksList[0-9]+.txt

	statusRoot: 		a directory to hold the tracking file for underway jobs.

	completionRoot: 	directory the tracking files for completed jobs

	statusRoot and completionRoot are created if they do not exist

Before using:

	edit this script and set up

	WORKS_SOURCE_HOME	Where the works live. Parent of folders named W......

	DRS_CODE_HOME		Where the DRS processing scripts live: typically,
						the subdirectory DRS-BATCH-PROCESSING of your local
						repository of
						https://github.com/BuddhistDigitalResourceCenter/drs-deposit

	BATCH_OUTPUT_HOME	Where completed batches go.
						Under this folder are Batch Builder projects, each one
						corresponding to one work list.

	BB_SOURCE				Location of the HUL Batch Builder executable.

	REQUIRES "bindirectory/SetBBLevel.sh" to be run

ENDUSAGE

}


# 
# Set up Batch builder home
#
function prepBBHome {
	# Copy BatchBuilder code to a location for this instance.
	# $MAKEDRS will copy the batchbuilder log to the
	# batch output directory
	export BB_HOME=$(mktemp -d)
	cp -rp $BB_SOURCE/* $BB_HOME
	rm -f $BB_HOME/logs/*

	propFile="$BB_HOME/conf/bb.properties" 
	[ -f $propFile ] && { rm -f $propFile ; }
	#
	# See <binFolder>/SetBBLevel.sh
	cp "${propFile}".${BB_LEVEL} "$propFile"
}


# Some constants
 WORKS_SOURCE_HOME=/Volumes/Archive
 DRS_CODE_HOME=/Users/jimk/drs-deposit/DRS-BATCH-PROCESSING
 BATCH_OUTPUT_HOME=/Volumes/DRS_Staging/DRS/prod/$(date +%Y%m%d)
 BB_SOURCE=/Users/jimk/DRS/BatchBuilder-2.2.13
 #
 # HACK: Magic phrase. Depends on ./splitWorks.sh
 WORKS_LIST_FN='worksList'
 #
 MAKEDRS='make-drs-batch.sh'
# for testing
 # MAKEDRS='touch-drs.sh'
# BATCH_OUTPUT_HOME=./testOut


ME=$(basename $0)

if (( $# != 3)); then
	Usage
	exit 1;
fi

[ -z "$BB_LEVEL" ] &&  { echo ${ME}':error:BB level not set' ; Usage ; exit 1; }

[ -e "$1" ] || { echo "${ME}":error: worksList file \'"$1"\' must exist but does not. ; exit 2; }
	# is the processing for this worksList underway?
     underFile=underway/${WORKS_LIST_FN}${x}
	[ -e $underFile ]  && { echo "${WORKS_LIST_FN}${x} already underway."; continue; }

statusRoot=$2
[ -d "$2" ] &&  { echo "${ME}":info: creating status directory  \'"$2"\'
				mkdir $2;
			 }
completionRoot=$3
[ -d "$3" ] &&  { echo "${ME}":info: creating completion directory  \'"$3"\'
				mkdir $3;
			 }

# build the output path
series=$(basename $1)
#
# Strip the extension
series="${series%.*}"
#
# get the number
x=${series#$(expr $WORKS_LIST_FN)}
# echo 'series:' $series
# echo 'x:' $x
# echo 'statusRoot:' $statusRoot
# echo 'completionRoot:' $completionRoot
# read

#
# Generate the batch path
[ ! -d  "${BATCH_OUTPUT_HOME}" ] && { mkdir -p ${BATCH_OUTPUT_HOME} ; }

batchPath=${BATCH_OUTPUT_HOME}/${series}.$(date +%H.%M)


#
# Set up the Batch builder level
prepBBHome

# Invoke the build in the background
 ${DRS_CODE_HOME}/${MAKEDRS} \
	"$1" ${DRS_CODE_HOME}/BB_tbrc/BB_tbrc2drs $batchPath \
	$WORKS_SOURCE_HOME ${BB_HOME} &
#
# Capture its pid and mark as underway
 thisRun=$!
#
# Mark as underway, with details
underFile=${statusRoot}/${WORKS_LIST_FN}${x}
 printf "%d_%s" $thisRun $(date +%H:%M:%S) > $underFile

 #
wait $thisRun

# Capture the batch's status.This is somewhat coarse grained, because
# the batch will continue after one has failed, so we need to look for batch.xml
# in the subdir
childRc=$?

# Write the status to the file
# cat ${doneFile} | awk \{ printf "%s_%d_%s" $0 $childRc  $(date +%H:%M:%S) \} #   >   ${resultsDir}/$doneFileName
#	set -x
#	cat ${doneFile} | awk -v newFields=$(printf "%d_%s" ${childRc} "$(date +%H:%M:%S)")  '{printf "!%s_%s@\n", $0, $newFields }' #   >   ${resultsDir}/$doneFileName
finishedArgs=$(printf "%d_%s" ${childRc} "$(date +%H:%M:%S)")
#
cat ${underFile} | awk -v newFields="${finishedArgs}"  '{printf "%s_%s\n", $0, newFields }'   >   ${completionRoot}/${WORKS_LIST_FN}${x}.$$
rm ${underFile}

rm -rf $BB_HOME

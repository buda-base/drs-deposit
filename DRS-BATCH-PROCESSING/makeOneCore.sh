#!/usr/bin/env bash



# Dont export. Override from caller
ME=$(basename $0)
# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

function Usage {
cat << ENDUSAGE
synopsis:
	${ME}  workListFileName statusRoot completionRoot

	worksListFileName: 	input source file


	statusRoot: 		a directory to hold the tracking file for underway jobs.

	completionRoot: 	directory the tracking files for completed jobs

	statusRoot and completionRoot are created if they do not exist

Before using:

	edit this script and set up

	WORKS_SOURCE_HOME	Where the works live. Parent of folders named <md5sum>/W....ttl

	BATCH_OUTPUT_HOME	Where completed batches go.
						Under this folder are Batch Builder projects, each one
						corresponding to one work list.

	BB_SOURCE				Location of the HUL Batch Builder executable.

	REQUIRES "bindirectory/SetBBLevel.sh" to be run

ENDUSAGE

}


source ${MEPATH}/commonUtils.sh

if (( $# != 3)); then
	Usage
	exit 1;
fi

[ -e "$1" ] || { echo "${ME}":error: data file \'"$1"\' must exist but does not. ; exit 2; }

statusRoot=$2
[ -d "$2" ] ||  { echo "${ME}":info: creating status directory  \'"$2"\'
				mkdir -p $2;
			 }

completionRoot=$3
[ -d "$3" ] ||  { echo "${ME}":info: creating completion directory  \'"$3"\'
				mkdir -p $3;
			 }

# build the status output path
series=$(basename $1)

# is the processing for this worksList underway?
underFile=${statusRoot}/${series}
[ -e $underFile ]  && { echo "${series} already underway.";  }

# read
#
# Generate the batch path
[ ! -d  "${BATCH_OUTPUT_HOME}" ] && { mkdir -p ${BATCH_OUTPUT_HOME} ; }

batchRoot=${BATCH_OUTPUT_HOME}/${series}.$(date +%H.%M)

#
# Set up the Batch builder temporary run home
prepBBHome

# Invoke the build in the background
  ${MAKEDRS} \
	"$1" $PROJECT_HOME $batchRoot \
	$WORKS_SOURCE_HOME ${BB_HOME}  &
#
# Capture its pid and mark as underway
thisRun=$!
#
# Mark as underway, with details
printf "%d_%s" $thisRun $(date +%H:%M:%S) > $underFile

 #
wait $thisRun

# Capture the batch's status.This is somewhat coarse grained, because
# the batch will continue after one has failed, so we need to look for batch.xml
# in the subdir
childRc=$?

finishedArgs=$(printf "%d_%s" ${childRc} "$(date +%H:%M:%S)")
#
cat ${underFile} | awk -v newFields="${finishedArgs}"  '{printf "%s_%s\n", $0, newFields }'   >   ${completionRoot}/${series}.$$
rm ${underFile}

rm -rf $BB_HOME

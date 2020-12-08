#!/usr/bin/env bash



# Dont export. Override from caller
ME=$(basename $0)
# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

function Usage {
cat << ENDUSAGE
synopsis:
	${ME}  workListFileName

	worksListFileName: 	input source file

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

source ${MEPATH}/validate.sh

if (( $# < 1 )); then
	Usage
	exit 1;
fi

[ -e "$1" ] || { echo "${ME}":error: data file \'"$1"\' must exist but does not. ; exit 2; }

# build the status output path
series=$(basename $1)


# read
#
# Generate the batch path
[ ! -d  "${BATCH_OUTPUT_HOME}" ] && { mkdir -p ${BATCH_OUTPUT_HOME} ; }

batchRoot=${BATCH_OUTPUT_HOME}/${series}.$(date +%H.%M)

#
# Set up the Batch builder temporary run home
prepBBHome

  ${MAKEDRS} \
	"$1" $PROJECT_HOME $batchRoot \
	$WORKS_SOURCE_HOME ${BB_HOME}  

# jimk: these accrete. tmp files have no auto deletion rule
cleanBBHome

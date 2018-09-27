#!/usr/bin/env bash

# This prologue has to precede every makeOnexxx

# Dont export
ME=$(basename $0)
# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"
[ -z "$BB_LEVEL" ] &&  { echo ${ME}':error:BB level not set' ; Usage ; exit 1; }

export WORKS_SOURCE_HOME=/Volumes/Archive
export BB_SOURCE=/Users/jimk/DRS/BatchBuilder-2.2.19
export PROJECT_HOME=${MEPATH}/BB_tbrc2drs
export MAKEDRS=${MEPATH}"/make-drs-batch.sh"
export BATCH_OUTPUT_HOME=/Volumes/DRS_Staging/DRS/${BB_LEVEL}/$(date +%Y%m%d)
 #
 #


${MEPATH}/makeOneCore.sh $@
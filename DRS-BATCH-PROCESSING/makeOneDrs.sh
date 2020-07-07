#!/usr/bin/env bash

# This prologue has to precede every makeOnexxx
# jimk: 2018-IX-28: BB_SOURCE now set in ~/bin/SetBBLevel.sh

# Dont export
ME=$(basename $0)
# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"


[ -z "$BB_LEVEL" ] &&  { echo ${ME}':error:BB level not set'  ; exit 1; }

# jimk drs-deposit #77 port to Debian
export WORKS_SOURCE_HOME=/mnt/rs5Archive
export PROJECT_HOME=${MEPATH}/BB_tbrc2drs
export MAKEDRS=${MEPATH}"/make-drs-batch.sh"
export BATCH_OUTPUT_ROOT=~/DRS_Builds/${BB_LEVEL}/
export BATCH_OUTPUT_HOME=${BATCH_OUTPUT_ROOT}$(date +%Y%m%d)
export BATCH_OUTPUT_PUBDIR=${BATCH_OUTPUT_ROOT}batchBuilds
 #

${MEPATH}/makeOneCore.sh $@

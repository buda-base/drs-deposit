#!/usr/bin/env bash

# This prologue has to precede every makeOnexxx
# jimk: 2018-IX-28: BB_SOURCE now set in ~/bin/SetBBLevel.sh

#
# return the top of the BatchBuild output tree
# eliminate need for RP$
function getBatchTop() {

    # Get the hostname
    host=$(hostname | tr '[:upper:]' '[:lower:]')

    # drop the domain
    host=${host%%.*}

    # these are specific to each server
    if [[ ${host} == "bodhi" ]] ; then
	bTop=/data/DRS
    else if [[ ${host} == "sattva" ]] ; then
		bTop=/home/DRS
	    else if [[ ${host} == "druk" ]] ; then
		bTop=/Volumes/DRS_Staging/DRS
	    else
		bTop=/dev/null
		 fi
	 fi
	 
    fi
    
    echo $bTop
    }
	     

# Dont export
ME=$(basename $0)
# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

[ -z "$BB_LEVEL" ] &&  { echo ${ME}':error:BB level not set'  ; exit 1 ;  }
export WORKS_SOURCE_HOME=/mnt/Archive
export PROJECT_HOME=${MEPATH}/BB_tbrc2drs
export MAKEDRS=${MEPATH}"/make-drs-batch.sh"
export BATCH_OUTPUT_ROOT=$(getBatchTop)/${BB_LEVEL}
export BATCH_OUTPUT_HOME=${BATCH_OUTPUT_ROOT}/$(date +%Y%m%d)
export BATCH_OUTPUT_PUBDIR=${BATCH_OUTPUT_ROOT}/batchBuilds

${MEPATH}/makeOneCore.sh $@

#!/usr/bin/env bash
#   Make one outline
#

# This prologue has to precede every makeOnexxx

# Dont export
ME=$(basename $0)

# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

[ -z "$BB_LEVEL" ] &&  { echo ${ME}':error:BB level not set' ; Usage ; exit 1; }

# Some constants
export WORKS_SOURCE_HOME=/Volumes/DRS_Staging/DRS/outlines
export PROJECT_HOME="${MEPATH}"/BB_tbrcOutline
export MAKEDRS="${MEPATH}"/make-drs-outline.sh
export BATCH_OUTPUT_HOME=/Volumes/DRS_Staging/DRS/${BB_LEVEL}/$(date +%Y%m%d)

${MEPATH}/makeOneCore.sh $@

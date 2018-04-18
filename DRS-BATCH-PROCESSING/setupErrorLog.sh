#!/bin/bash
#  Shell script insert to set up error logging
#  INPUTS:    	$ME: the name of the calling script
#  OUTPUTS:   	$ERR_LOG: path to the log file
#
#  GLOBALS:   	Uses $HOME/DRS/log as the parent of the log files.
#				Creates if needed.
#				 
### Generate a dated log file name
export DRS_LOG_DIR="${HOME}/DRS/log/"
export ERROR_TXT="error"
export INFO_TXT="info"
export FATAL="FATAL"
export LOG_DATE_FMT="%DT%T"
# 
# Watch parallel
ERR_LOG_NAME="${1}$(date +%F.%H.%M.%S).$$.log"
ERR_LOG="${DRS_LOG_DIR}${ERR_LOG_NAME}"
[ -d $DRS_LOG_DIR ] || { 
	errstr="${1}:${INFO_TXT}: ${DRS_LOG_DIR} does not exist. Creating it"
	mkdir $DRS_LOG_DIR
	rc=$?
	[ $rc == "0" ] || { echo "$(logDate) ${1}:${FATAL}:Cannot create ${DRS_LOG_DIR}." ; exit 5 ;}

	echo $errstr 2>&1 | tee -a $ERR_LOG 
}

function logDate() {
	echo $(date +$LOG_DATE_FMT )
}
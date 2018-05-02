#!/bin/bash
# jimk 2018 IV 16
#
# Execute an SFTP batch
#
# Variables and structure from ftpScript.sh
ME=$(basename $0)
ME_DIR=$(dirname $0)


#section error logging. Requires trailing
# Output is var ERR_LOG, ERROR_TXT, INFO_TXT variables
. ${ME_DIR}/setupErrorLog.sh "${ME}"
#endsection Set up logging

#section I
export ME_PPK='/Users/jimk/ppk/DrsDropQa.ppk'

export DRS_DROP_HOST=drs2drop.lib.harvard.edu

export BASE_REMOTE_DIR="incoming/"

# LOADREPORT is the prefix, suffixes vary
export SUCCESS_FILE_NAME="batch.xml"

export FAIL_FILE_NAME=${SUCCESS_FILE_NAME}.failed


usage() {
	cat <<  USAGE
Usage: ${ME} scriptDirectory remoteUser 
where
 	scriptDirectory contains one or more sftp batch scripts in \'directory\' 
 	remoteUser		is the user account on the remote system
USAGE

}



sourcePath=${1?Script directory not given. $(usage)}
# Does the input exist?
[ -d "$sourcePath" ] || { 
	echo "${ME}:${ERROR_TXT}:directory ${targetList} not found." 2>&1 | tee -a $ERR_LOG ;  
	exit 2 ;  
}

drsDropUser=${2?Remote User not given. $(usage)}

# Loop over all the batch.xml.failed in this directory
for sftpBatch in ${sourcePath}/* ; do

	sftp -oLogLevel=VERBOSE -b ${sftpBatch} -i $ME_PPK ${drsDropUser}@${DRS_DROP_HOST}:${BASE_REMOTE_DIR} 2>&1 | tee -a $ERR_LOG ;  

	rc=$?

	errx=$(printf "sftp $DRS_DROP_HOST $drsDropUser to $sftpBatch ") ;
	[ $rc == 0 ] && { 
		echo "${ME}:${INFO_TXT}: $errx" 2>&1 | tee -a $ERR_LOG ; 
	} 

	[ $rc == 0 ] || { 
		echo $errx  | tee -a $ERR_LOG ;  
		echo "${ME}:${ERROR_TXT}: $errx failed $rc" 2>&1 | tee -a $ERR_LOG ; 
	} 


done




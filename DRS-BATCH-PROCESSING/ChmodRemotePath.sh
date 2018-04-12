#!/bin/bash
# jimk 2018 III 27
#
# poll a server for logs
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

# DRS_DROP_USER=drs2_tbrctest
# export DRS_DROP_USER

usage() {
	cat <<  USAGE
Usage: ${ME} directory remoteUser 
where
 	directory contains one or more batchWnnnn-n"$FAIL_FILE_NAME" files, which are
 				under the sftp account of remoteUser.
 	remoteUser		is the user on the remote system who owns the files.
USAGE

}

# If running in parallel, cant collide
SFTP_CMD_FILE=$( mktemp .sftpXXXXXX ) || { echo ${ME}:${ERROR_TXT}: Cant create command file ; exit 1 ; } 


# do we have what we need?



sourcePath=${1?$(usage)}
# Does the input exist?
[ -d "$sourcePath" ] || { 
	echo "${ME}:${ERROR_TXT}:directory ${targetList} not found." 2>&1 | tee -a $ERR_LOG ;  
	exit 2 ;  
}

#
# Build a script for remote ftp to execute
#
# args:
# $1: name of good file
# $2: name of failed batch file (local)
# $3: local file location
# $4: remote directory to work in
# 
buildSFTPBatch() {
	_successPath=$1
	_failPath=$2
	_localPath=$3
	_remotePath=$4

	# the - prefix in the sftp commands allows continuation 
	# on command failure.
	# The renames are because
	# success case: we can't guarantee the LOADREPORT has a known file name
	# Fortunately, this works only when there's only 1 LOADREPORT
	# in the remote frp directory
	# failure case: all files are named batch.xml.failed
	cat << EFTP > ${SFTP_CMD_FILE}
		chmod 775 $_remotePath
EFTP
}

mkdir $sourcePath/recovery

export drsDropUser=${2?${ME}:${ERROR_TXT}: remote user is not given. $(${0}) }

# Loop over all the batch.xml.failed in this directory
find $sourcePath -name \* | while read targetDir ; do

	# pollDRS renames a fail file BatchWxxxxx-1_batch.xml.failed.
	targetDir=$(basename $targetDir)
	buildSFTPBatch "$SUCCESS_FILE_NAME" "$FAIL_FILE_NAME" $sourcePath $targetDir
	
	# cat $SFTP_CMD_FILE
	sftp -oLogLevel=VERBOSE -b ${SFTP_CMD_FILE} -i $ME_PPK ${drsDropUser}@${DRS_DROP_HOST}:${BASE_REMOTE_DIR}  | tee -a $ERR_LOG ;  

	rc=$?

cat ${SFTP_CMD_FILE}
	[ $rc == 0 ] && { 
		echo "${ME}:${INFO_TXT}: sftp $DRS_DROP_HOST $sourcePath to $targetDir success" 2>&1 | tee -a $ERR_LOG ; 
	} 

	[ $rc == 0 ] || { 
		errx=$(printf "${ME}:${ERROR_TXT}: sftp $DRS_DROP_HOST $sourcePath to $targetDir failed: code $rc") ;
		echo $errx  | tee -a $ERR_LOG ;  
		# jsk 20180406: keep going. One failure is not catastrophic
		# Usually just means an upload has occurred
		# exit $rc ; 
	}

	[ -e $SFTP_CMD_FILE ] && rm -f $SFTP_CMD_FILE
done




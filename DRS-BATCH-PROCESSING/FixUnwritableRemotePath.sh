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
Usage: ${ME} remoteUser 
where
 	remoteUser		is the user on the remote system who owns the files.
	list of remote directories is read from input
USAGE

}

# If running in parallel, cant collide
SFTP_CMD_FILE=$( mktemp .sftpXXXXXX ) || { echo ${ME}:${ERROR_TXT}: Cant create command file ; exit 1 ; } 


[ "$1" == "-h" ] && { usage ; exit 1;}

# do we have what we need?
drsDropUser=${1?${ME}:${ERROR_TXT}:Remote user not given.}

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
	_remotePath=$3

	cat << EFTP > ${SFTP_CMD_FILE}
		cd  $_remotePath
		rename $_successPath $failPath
EFTP
}


export drsDropUser=${2?${ME}:${ERROR_TXT}: remote user is not given. $(${0} -h) }

 while read targetDir ; do

	# accomodate a list of paths
	targetDir=$(basename $targetDir)
	buildSFTPBatch "$SUCCESS_FILE_NAME" "$FAIL_FILE_NAME" $targetDir
	
	sftp -oLogLevel=VERBOSE -b ${SFTP_CMD_FILE} -i $ME_PPK ${drsDropUser}@${DRS_DROP_HOST}:${BASE_REMOTE_DIR}  2>&1 | tee -a $ERR_LOG ;  

	rc=$?
	
	errx ="$(logDate) ${ME}:${INFO_TXT}: sftp $drsDropUser  $DRS_DROP_HOST to $targetDir ";
	
	[ $rc == 0 ] && { 
		echo $errx success | tee -a $ERR_LOG ; 
	} 

	[ $rc == 0 ] || { 
		echo $errx failed rc = $rc  | tee -a $ERR_LOG ;  
		# jsk 20180406: keep going. One failure is not catastrophic
		# Usually just means an upload has occurred
		# exit $rc ; 
	}

	[ -e $SFTP_CMD_FILE ] && rm -f $SFTP_CMD_FILE
done




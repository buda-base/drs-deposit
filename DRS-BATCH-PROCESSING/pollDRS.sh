#!/bin/bash
#
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
export SUCCESS_PATH="LOADREPORT"

export FAIL_PATH=batch.xml.failed

# DRS_DROP_USER=drs2_tbrctest
# export DRS_DROP_USER

usage() {
	cat <<  USAGE
Usage: ${ME} listToUpload remoteUser reportDir where
 	listToUpload	is the file list containing the list of directories.
 					This file can be the same as the upload list (/path/to/batches/batchnnn-1)
 					or it can be just a list of batches (BatchW.....-1)
 	remoteUser		is the user on the remote system
 	reportDir		is the directory which will receive the remote logs
USAGE

}

# If running in parallel, cant collide
SFTP_CMD_FILE=$( mktemp .sftpXXXXXX ) || { echo ${ME}:${ERROR_TXT}: Cant create command file ; exit 1 ; } 


# do we have what we need?


[ "x$1" == "x" ] && { echo  "${ME}:${ERROR_TXT}:List to search for not given."  ; usage ; exit 1; }

targetList=${1?$(usage)}
# Does the input exist?
[ -f "$targetList" ] || { 
	echo "${ME}:${ERROR_TXT}:listToUpload ${targetList} is not a file or does not exist" ; 
	exit 2 ;  
}

#
# Build a script for remote ftp to execute
#
# args:
# $1: source directory
# $2: target directory
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
		lcd $_localPath
		cd $_remotePath
        -mget -P ${_successPath}* ${_remotePath}_${_successPath}
        -get -P $_failPath ${_remotePath}_${_failPath}
EFTP
}

export drsDropUser=${2?${ME}:error: remote user is not given. $(${0}) }

export reportDir=${3?${ME}:error: report directory not given. $(usage)}

# make report dir if not exists
[ ! -d $reportDir ] && { echo "${ME}:${INFO_TEXT}: $reportDir not found. Creating." ; mkdir -p $reportDir ; }

while read targetSearch ; do
	buildSFTPBatch "$SUCCESS_PATH" "$FAIL_PATH" $reportDir $(basename $targetSearch)
	sftp -oLogLevel=VERBOSE -b ${SFTP_CMD_FILE} -i $ME_PPK ${drsDropUser}@${DRS_DROP_HOST}:${BASE_REMOTE_DIR}  2>> $ERR_LOG
done < $targetList


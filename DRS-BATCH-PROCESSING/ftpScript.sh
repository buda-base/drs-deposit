#!/bin/bash

#######################################################################
#
# transfers a set of batches to a remote system.
# The destination is a system which triggers a process when a well-know file is uploaded
# AND the sender disconnects the ftp session
#
#
# Arguments
#
#	listToUpload:		The parent of the directories containing batches.
#	remoteUser:			The credential of the remote user
#
#
# Monitoring
#	Errors are logged to ~/DRS/log/ftpScript.sh<yyyy-mm-dd.hh.mm>.log
#
#section 
ME=$(basename $0)
ME_DIR=$(dirname $0)

#section I
ME_PPK='/Users/jimk/ppk/DrsDropQa.ppk'
export ME_PPK
DRS_DROP_HOST=drs2drop.lib.harvard.edu
export DRS_DROP_HOST

# DRS_DROP_USER=drs2_tbrctest
# export DRS_DROP_USER

#section error logging. Requires trailing
# Output is var ERR_LOG, ERR_TEXT, INFO_TEXT variables
. ${ME_DIR}/setupErrorLog.sh "${ME}"
#endsection Set up logging

usage() {
	cat <<  USAGE
Usage: ${ME} listToUpload remoteUser  where
 	listToUpload	is the file list containing the upload paths.
 					Each line contains a directory to upload
 	remoteUser		is the user on the remote system

 	[dropbox ]		optional: DRS Dropbox address. Uses PROD as default
USAGE
}

# If running in parallel, cant collide
SFTP_CMD_FILE=$( mktemp .sftpXXXXXX ) || { echo ${ME}:error: Cant create command file ; exit 1 ; } 

#
# Build a script for remote ftp to execute
#
# args:
# $1: source directory
# $2: target directory
# 
buildSFTPBatch() {
	_sourcePath=$1
	_targetPath=$2
	[ -e $SFTP_CMD_FILE ] && rm -f $SFTP_CMD_FILE
	# the - prefix allows continuation on command failure.
	# sftp rmdir builtin may fail if directory is not empty.
    echo "-rmdir $_targetPath" >> ${SFTP_CMD_FILE}
	# you have to make the directory, and then put stuff in it. here,
	# $remoteTarget must be the last directory in the path $b 
	echo "mkdir $_targetPath" >> ${SFTP_CMD_FILE}
	echo "put -r -P $_sourcePath" >> ${SFTP_CMD_FILE}
	# operations are relative to the directory in the command line ":incoming"
	# jimk Probably not needed: ingestion waits for upload to disconnect
	# echo "rename ${1}/${BATCH_XML}${WAIT_SUFFIX} ${bTarget}/$BATCH_XML" >> ${SFTP_CMD_FILE}
	#
	# jimk: See of this helps with JDBC connection errors, and fole missing files
	echo "!sleep 2" >> ${SFTP_CMD_FILE}
}


# do we have what we need?

[ "x$1" == "x" ] && { usage ; exit 1; }

targetList="$1"
# Does the input exist?
[ -f "$targetList" ] || { 
	echo "${ME}:${ERROR_TXT}:listToUpload ${targetList} is not a file or does not exist" ; 
	exit 2 ;  
}

drsDropUser=${2?${ME}:error: remote user is not given}

drsDropHost=${3:-$DRS_DROP_HOST}



#endsection setup and arg parse
while read sourcePath ; do
	targetPath=$(basename $sourcePath)

	buildSFTPBatch "$sourcePath" "$targetPath" 

	# Clean up this batch only. If the dir exists, ftp wont be able to clean it up
	# If this fails, the ftp wwont work, and the fail will be logged
	# Were not force removing the file anymore. No context, since we moved the 
	# processing loop into buildSftpBatch
	# -n flag for use in read loop
	# ssh -n -i $ME_PPK -l $DRS_DROP_USER $drsDropHost  rm -rf incoming/${remoteTarget}

	sftp -oLogLevel=VERBOSE -b ${SFTP_CMD_FILE} -i $ME_PPK ${drsDropUser}@${drsDropHost}:incoming/   2>> $ERR_LOG


	rc=$?

[ $rc == 0 ] && { echo "${ME}:${INFO_TEXT}: sftp $drsDropHost $targetPath success" >> $ERR_LOG ; } 
	# rm ${SFTP_CMD_FILE}
	[ $rc == 0 ] || { 
		errx=$(printf "${ME}:${ERROR_TXT}: sftp $drsDropHost $targetPath failed: code $rc") ;
		echo $errx;
		echo $errx >> $ERR_LOG;
		# jsk 20180406: keep going. One failure is not catastrophic
		# Usually just means an upload has occurred
		# exit $rc ; 
	}

	[ -e $SFTP_CMD_FILE ] && rm -f $SFTP_CMD_FILE

done < $targetList

##############################################
#
# Save this section in case we ever need to use expect
# ~/tmp/ssh.expect joBeetz@somewhere.over.the.rainbow -p 15366  jojosMill "rm -rf incoming/${remoteTarget}"
# expect -d -c "
# 	set timeout 60
# 	spawn sftp -b ${SFTP_CMD_FILE} -oLogLevel=DEBUG -P 15366  joBeetz@inner.tbrc.org:incoming/
# 	expect yes/no { send yes\r; 
# 			expect *assword: { send jojosMill\r }
# 	} "*assword:" { send jojosMill\r }	
# 	# expect *assword: { send jojosMill\r }	
# 	expect sftp> send {ls\r}	
# 	expect sftp> send {quit\r}
# "

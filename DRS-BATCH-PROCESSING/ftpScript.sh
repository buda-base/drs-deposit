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
DRS_DROP_HOST=drs2drop-qa.hul.harvard.edu
export DRS_DROP_HOST
DRS_DROP_USER=drs2_tbrctest
export DRS_DROP_USER

# If running in parallel, cant collide
SFTP_CMD_FILE=$( mktemp .sftpXXXXXX ) || exit 1 

#section error logging. Requires trailing
# Output is var ERR_LOG, ERR_TEXT, INFO_TEXT variables
. ${ME_DIR}/setupErrorlog.sh "${ME}"
#endsection Set up logging

usage() {
	cat <<  USAGE
Usage: ${ME} listToUpload  where
 	listToUpload		is the file list containing the upload paths. Each line contains a directory
 						to upload
USAGE
exit 1;
}

#
# Build a script for remote ftp to execute
#
# args:
# $1: list of directories we need to upload
# 
buildSFTPBatch() {

	[ -e $SFTP_CMD_FILE ] && rm -f $SFTP_CMD_FILE
	while read sourcePath ; do
		targetPath=$(basename $sourcePath)
		# the - prefix allows continuation on command failure.
		# sftp rmdir builtin may fail if directory is not empty.
		# The script should have removed the directory with ssh
	    echo "-rmdir $targetPath" >> ${SFTP_CMD_FILE}
		# you have to make the directory, and then put stuff in it. here,
		# $remoteTarget must be the last directory in the path $b 
		echo "mkdir $targetPath" >> ${SFTP_CMD_FILE}
		echo "put -r $sourcePath" >> ${SFTP_CMD_FILE}
		# operations are relative to the directory in the command line ":incoming"
		# jimk Probably not needed: ingestion waits for upload to disconnect
		# echo "rename ${1}/${BATCH_XML}${WAIT_SUFFIX} ${bTarget}/$BATCH_XML" >> ${SFTP_CMD_FILE}
	done < $1
}


# do we have what we need?
[ "x$1" == "x" ] && usage

# Does the input exist?
[ -f "$1" ] || { 
	echo "${ME}:${ERROR_TXT}:listToUpload "$1" is not a file or does not exist" ; 
	exit 2 ;  
}

targetList="$1"

#endsection setup and arg parse

buildSFTPBatch $targetList

# Clean up this batch only. If the dir exists, ftp wont be able to clean it up
# If this fails, the ftp wwont work, and the fail will be logged
# Were not force removing the file anymore. No context, since we moved the 
# processing loop into buildSftpBatch
# -n flag for use in read loop
# ssh -n -i $ME_PPK -l $DRS_DROP_USER $DRS_DROP_HOST  rm -rf incoming/${remoteTarget}

sftp -oLogLevel=VERBOSE -b ${SFTP_CMD_FILE} -i $ME_PPK ${DRS_DROP_USER}@${DRS_DROP_HOST}:incoming/   2>> $ERR_LOG

[ -e $SFTP_CMD_FILE ] && rm -f $SFTP_CMD_FILE

rc=$?
# rm ${SFTP_CMD_FILE}
[ $rc == 0 ] || { 
	errx=$(printf "${ME}:${ERROR_TXT}: sftp $DRS_DROP_HOST failed: code $rc") ;
	echo $errx;
	echo $errx >> $ERR_LOG;
	exit $rc ; 
}

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
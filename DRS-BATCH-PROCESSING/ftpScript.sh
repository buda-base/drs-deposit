#!/bin/bash

#######################################################################
#
# transfers a set of batches to a remote system.
# The destination is a system which triggers a process when a well-know file is uploaded:
# This script inhibits the upload by temporarily renaming the well known file
# to something else.
#
# After the transder succeeds, the file is named back to the original name, which
# triggers the remote process.
# If a transfer fails, you can use the companion unWait.sh to rename the files back.
#
# Arguments
#
#	sourceRoot:		The parent of the directories containing batches.
#
#	batchDirPattern:(optional)The template for the name of the directories which contain batches.
#					the default is "batchW*".  note the pattern name is a globbing construct
#
# Monitoring
#	Errors are logged to ~/DRS/log/ftpScript.sh<yyyy-mm-dd.hh.mm>.log
#
#section 
ME=$(basename $0)

#section

#section error logging. Requires trailing /
. ./setupErrorlog.sh "${ME}"
#endsection Set up logging

usage() {
	 printf "\b\nUsage: ${ME} sourceRoot [opt: batchDirPattern ]  where\
\n\t sourceRoot\t\tis the parent directory of batches to be uploaded\
\n\t batchDirPattern\toverrides the default prefix of subdirectory names\
\n\t\t\t\tof sourceRoot which contain batches.\
\n\t\t\t\tdefault prefix is 'batchW*'\n\n"; 
exit 1;
}

buildSFTPBatch() {
		# the - prefix allows continuation on command failure.
		# sftp rmdir builtin may fail if directory is not empty.
	    echo "-rmdir $bTarget" > .sftpBatch
		# you have to make the directory, and then put stuff in it. here,
		# $bTarget must be the last directory in the path $b 
		echo "mkdir $bTarget" >> .sftpBatch
		echo "put -r $b" >> .sftpBatch
		# operations are relative to the directory in the command line ":incoming"
		echo "rename ${bTarget}/${BATCH_XML}${WAIT_SUFFIX} ${bTarget}/$BATCH_XML" >> .sftpBatch
}

# do we have what we need?
[ "x$1" == "x" ] && usage

# Does the input exist?
[ -d "$1" ] || { 
	echo "${ME}: $ERROR sourceRoot "$1" is not a directory or does not exist" ; 
	exit 2 ;  
} 

#endsection setup and arg parse

DEFAULT_BATCH_DIR_PATTERN="batchW*"
BATCH_DIR_PATTERN=$DEFAULT_BATCH_DIR_PATTERN
BATCH_XML=batch.xml
WAIT_SUFFIX=".wait"

# override default batch dir pattern
[ "x$2" ==  "x" ] ||  BATCH_DIR_PATTERN=$2 ;

# For each batch

BATCH_ROOT=${1}/$BATCH_DIR_PATTERN

for b in ${BATCH_ROOT} ; do # rm /* it goes one level too deep
	bTarget=$(basename $b)
	 [ -f $b/$BATCH_XML ] && mv $b/$BATCH_XML $b/${BATCH_XML}${WAIT_SUFFIX}

buildSFTPBatch

# Clean up this batch only
# If this fails, the ftp wwont work, and the fail will be logged
ssh -i /Users/jimk/ppk/rootAtWeyrSSH.ppk -l jimk inner.tbrc.org  -p 15366  rm -rf incoming/${bTarget}

sftp -oLogLevel=ERROR -b .sftpBatch -P 15366 -i /Users/jimk/ppk/rootAtWeyrSSH.ppk jimk@inner.tbrc.org:incoming/  2>> ftp.log
rc=$?
rm .sftpBatch
[ $rc == 0 ] || { 
	errx=$(printf "${ME}: ${ERROR}: sftp $bTarget failed: code $rc") ;
	echo $errx;
	echo $errx >> $ERR_LOG;
	exit $rc ; 
}
done

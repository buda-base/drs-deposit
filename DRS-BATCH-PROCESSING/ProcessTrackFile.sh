#!/bin/bash
#
# Transform a UploadTrack file to a shell script

export ME=$(basename $0)
function usage() {
	cat << USAGE
	Synopsis: $ME [ -h | execFile trackFile ]
	execFile is the command to run against the lines in 
	trackFile.

	see makeOneFtp.sh for trackFile syntax. Here it is
	ftpUserName.sourceFileName, where the makeOneFtp.sh writer
	stupidly used . as a separator.
USAGE
}
 
 [ "$1" == "-h" ] && { usage ; exit 1; }
execFile=${1?Command not given. see $ME -h}
trackFile=${2?track file not given. See $ME -h}

awk -v command=$execFile -v execFile=${execFile}  -F'[|.]' 'BEGIN{ ftpN = 0} {print execFile , $2"."$3 , $1,"reports/ftp" ftpN ; ftpN += 1 }' ${trackFile} | sed 's/ftp0/ftp/' | sort -u

#! /bin/bash
#   Make one Ftp Launch, with tracking control
#
# arguments:

#
function Usage {
cat << ENDUSAGE
synopsis:
${ME}  batchDirPath statusRoot completionRoot remoteUserName

batchDirPath: 		Path to a file containing a list of folders to upload

statusRoot: 		a directory to hold the tracking file for underway jobs.

completionRoot: 	directory the tracking files for completed jobs

remoteUserName		credential for remote system

remotePath		(optional) remote host name (for QA)

statusRoot and completionRoot are created if they do not exist

ENDUSAGE
}


# Some constants
FTPSCRIPT='ftpScript.sh'

ME=$(basename "$0" )

if (( $# <  4)) || (( $# > 6)) ; then
  echo nargs: $#
  echo args  "$@"
Usage
exit 1;
fi

[ -f "$1" ] || { echo "${ME}":error: source list  \'"$1"\' must exist but does not. ; exit 2; }
srcListPath=$1
srcListName=$(basename "$1" )

statusRoot=$2
[ -d "$statusRoot" ] &&  { echo "${ME}":info: creating status directory  \'"$2"\'
			mkdir $statusRoot ;
		 }
# container for status of underway jobs
underFile=${statusRoot}/${srcListName}

[ -e $underFile ]  && { echo "${ME}":error:"${srcListName} already underway."; exit 5; }			 

# container for status of completed jobs
completionRoot=$3
[ -d "$3" ] &&  { echo "${ME}":info: creating completion directory  \'"$3"\'
			mkdir $3;
		 }


remoteUserName=${4?${ME}:error: remote User Name not given}

remoteHost=$5

# Invoke the upload in the background


# jimk: with parallel, we dont need this overhead
${FTPSCRIPT} $srcListPath $remoteUserName $remoteHost

exit

${FTPSCRIPT} $srcListPath $remoteUserName $remoteHost &

# Capture its pid and mark as underway
thisRun=$!

#
# Mark as underway, with details
printf "%d_%s" "$thisRun" $(date +%H:%M:%S) >> $underFile

 #
wait $thisRun

# Capture the upload status. Unlike drs-batch, ftp upload
# quits on first failure
# in the subdir
childRc=$?

# Write the status to the file
# cat ${doneFile} | awk \{ printf "%s_%d_%s" $0 $childRc  $(date +%H:%M:%S) \} #   >   ${resultsDir}/$doneFileName
#	set -x
#	cat ${doneFile} | awk -v newFields=$(printf "%d_%s" ${childRc} "$(date +%H:%M:%S)")  '{printf "!%s_%s@\n", $0, $newFields }' #   >   ${resultsDir}/$doneFileName
finishedArgs=$(printf "%d_%s" ${childRc} "$(date +%H:%M:%S)")
#

#
# jimk: 2018-03-27: need to associate the drs user with the batch.

echo 

cat $underFile | awk -v newFields="${finishedArgs}|TRACK|${remoteUserName}_${srcListPath}"  '{printf "%s_%s\n", $0, newFields }'   >   ${completionRoot}/${srcListName}.$$
rm $underFile

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
#	remoteHost (optional)	The remote host (generally for QA)
#
#
# Monitoring
#	Errors are logged to ~/DRS/log/ftpScript.sh<yyyy-mm-dd.hh.mm>.log
#
#section


ME=$(basename "$0")
ME_DIR=$(dirname "$0")

#section I
export ME_PPK='/Users/jimk/ppk/DrsDropQa.ppk'
export DRS_DROP_HOST=drs2drop.lib.harvard.edu

# DRS_DROP_USER=drs2_tbrctest
# export DRS_DROP_USER

#section error logging. Requires trailing
# Output is var ERR_LOG, ERROR_TXT, INFO_TEXT variables
# shellcheck disable=SC1090
. "${ME_DIR}"/setupErrorLog.sh "${ME}"
#endsection Set up logging

usage() {
  cat <<USAGE
Usage: ${ME} listToUpload remoteUser [dropbox ]  where

 	listToUpload	is the file list containing the upload paths.
 					Each line contains a directory to upload
 	remoteUser		is the user on the remote system

 	[dropbox ]		optional: DRS Dropbox host . Uses PROD as default
st
USAGE
}

# If running in parallel, cant collide
SFTP_CMD_FILE=$(mktemp .sftpXXXXXX) || {
  echo "${ME}":error: Cant create command file
  exit 1
}

export BATCH_XML=batch.xml
export BATCH_XML_WAIT=${BATCH_XML}.wait

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
  # the - prefix allows continuation on command failure.
  # sftp rmdir builtin may fail if directory is not empty.
  # you have to make the directory, and then put stuff in it. here,
  #
  # if the mkdir fails, we must bail. The directory already exists.

  # $remoteTarget must be the last directory in the path $b
  # And sourcePath's last node must be targetPath
  # operations are relative to the directory in the command line ":incoming"
  #
  # jimk: See of this helps with JDBC connection errors, and  missing files
  # jimk 2018 04 16: this might help with missing files
  # by inhibiting ingestion until every file is found.
  # Note the caller is responsible for creating and removing the wait file
  # jimk:  take 2. Don't quit until the whole run is built, not each folder in the run.
  cat <<EFTP >> "$SFTP_CMD_FILE"
	-rmdir $_targetPath
	mkdir $_targetPath
	put -r -P $_sourcePath
	cd $_targetPath
	rename ${BATCH_XML_WAIT} ${BATCH_XML}
EFTP
}

# do we have what we need?

[[ -z "$1" ]] && {
  usage
  exit 1
}

targetList="$1"
# Does the input exist?
[ -f "$targetList" ] || {
  echo "${ME}:${ERROR_TXT}:listToUpload ${targetList} is not a file or does not exist"
  exit 2
}

drsDropUser=${2?${ME}:error: remote user is not given}

drsDropHost=${3:-$DRS_DROP_HOST}

#endsection setup and arg parse
while read -r sourcePath; do
  targetPath=$(basename "$sourcePath")

  buildSFTPBatch "$sourcePath" "$targetPath"

  # Clean up this batch only. If the dir exists, ftp wont be able to clean it up
  # If this fails, the ftp wont work, and the fail will be logged
  # Were not force removing the file anymore. No context, since we moved the
  # processing loop into buildSftpBatch
  # -n flag for use in read loop
  # ssh -n -i $ME_PPK -l $DRS_DROP_USER $drsDropHost  rm -rf incoming/${remoteTarget}

  # jimk 2018 IV 16: maybe help missing files
  # Inhibit batch ingestion until all files are loaded

  mv "$sourcePath"/$BATCH_XML "$sourcePath"/$BATCH_XML_WAIT

done <"$targetList"

# Maybe wont fail so often if we do all our uploads then quit
printf "quit\n" >>"${SFTP_CMD_FILE}"

cat "${SFTP_CMD_FILE}"
echo "${SFTP_CMD_FILE}"

# sftp -oLogLevel=VERBOSE -b ${SFTP_CMD_FILE} -i $ME_PPK ${drsDropUser}@${drsDropHost}:incoming/ 2>&1 | tee -a $ERR_LOG

rc=$?

# and clean up
while read -r sourcePath; do
  mv "$sourcePath"/$BATCH_XML_WAIT "$sourcePath"/$BATCH_XML
done <"$targetList"

errx=" sftp $drsDropHost $drsDropUser $targetPath "

[ $rc == 0 ] && {
  echo "$(logDate) ${ME}:${INFO_TXT}:  $errx success" | tee -a "$ERR_LOG"
}
[ $rc == 0 ] || {

  echo "$(logDate) ${ME}:${ERROR_TXT}:  $errx fail $rc " | tee -a "$ERR_LOG"
  # jsk 20180406: keep going. One failure is not catastrophic
  # Usually just means an upload has occurred
  # exit $rc ;
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

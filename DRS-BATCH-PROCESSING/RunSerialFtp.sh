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
  cat <<USAGE
Usage: ${ME} scriptDirectory remoteUser 
where
 	scriptDirectory contains one or more sftp batch scripts in \'directory\' 
 	remoteUser		is the user account on the remote system
USAGE

}

sourcePath=${1?Script directory not given. $(usage)}
# Does the input exist?
[ -d "$sourcePath" ] || {
  echo "${ME}:${ERROR_TXT}:directory ${targetList} not found." 2>&1 | tee -a $ERR_LOG
  exit 2
}

drsDropUser=${2?Remote User not given. $(usage)}

# Loop over all the batches in this directory.
#
# jimk 2020.10.16: DRS really doesn't like it when a n sftp connection is closed and then
# reopened. so, since this is for a user, serialize all the commands into one,
# and let the connection close when sftp is done, or insert one quit

sumsftp=$(mktemp -p . --suffix=.sftp .sftp-$(date +%H-%M-%S)-XXX)
cat ${sourcePath}/* >"${sumsftp}"
echo "quit" >>"${sumsftp}"
 sftp -oLogLevel=VERBOSE -b "${sumsftp}" -i $ME_PPK ${drsDropUser}@${DRS_DROP_HOST}:${BASE_REMOTE_DIR} 2>&1 | tee -a $ERR_LOG
rc=$?
errx=$(printf "sftp %s %s to %s"  "$DRS_DROP_HOST" "$drsDropUser" "${sumsftp}" )
if [[ $rc == 0 ]] ;then
  echo "${ME}:${INFO_TXT}: $errx" 2>&1 | tee -a $ERR_LOG
else
  echo $errx | tee -a $ERR_LOG
  echo "${ME}:${ERROR_TXT}: $errx failed $rc" 2>&1 | tee -a $ERR_LOG
fi

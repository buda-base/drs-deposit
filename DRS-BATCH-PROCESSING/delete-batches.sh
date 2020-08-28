#!/usr/bin/env bash
#
# Recovery mode
#
# Assume a mailerrs.txt

export ME=$(basename $0)
export ME_DIR=$(dirname $0)
. ~/bin/setupErrorLog.sh

## HACK ALERT: This var is the same as in deleteAlreadyDepositedSFTP.sh
targetErrRE="Object owner supplied name" #  .* already exists for owner code"

# Assume these files exist
MAIL_TXT=mailerrs.txt
#
# ${ME} creates these files
MAIL_DAT=mailerrs.dat
UPLOAD_TRACK=${1?"usage: $ME uploadTrackingFileName BuildListSpec"}

# debug: input list for main loop:
# parseMail.awk $MAIL_TXT | grep -v "${targetErrRE}" $MAIL_DAT | cut -f3,4 -d'|' | sort -u  -k1 -t'|'

# get the user and the batch name from the mail errors, look up the build list
# in the upload track.
# get the batch path from the build list file
while IFS='|'  read -a aLine ; do

  user=${aLine[0]}
  batchName=${aLine[1]}

# -w because sometimes users are subsets of other users
  buildList=$(grep -w ${user} "$UPLOAD_TRACK" | cut -f2 -d'|' | sort -u)

  batchPath=$(grep "${batchName}" "$buildList" | cut -f2 -d'|' | sort -u)

  # echo ${user}':'${batchName}':'${buildList}':'${batchPath}':' len is ${#aLine[@]}

  printf "Updating DB for ${batchPath}.."
  updateBuildStatus -d prod:~/.drsBatch.config "$batchPath" FAIL
  printf "removing path...."
  rm -rf "$batchPath"
  printf "done\n"
done < <(parseMail.awk $MAIL_TXT | grep -v "${targetErrRE}" $MAIL_DAT | cut -f3,4 -d'|' | sort -u -k1 -t'|')


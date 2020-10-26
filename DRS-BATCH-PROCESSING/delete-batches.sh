#!/usr/bin/env bash
#
# Recovery mode
#
# Assume a mailerrs.txt

# shellcheck disable=SC2155
export ME=$(basename "$0")
export ME_DIR=$(dirname "$0")
# shellcheck disable=SC1090
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
while IFS='|' read -ra aLine; do

  user=${aLine[0]}
  batchName=${aLine[1]}

  # -w because sometimes users are subsets of other users
  buildList=$(grep -w "${user}" "$UPLOAD_TRACK" | cut -f2 -d'|' | sort -u)

  batchPath=$(grep "${batchName}" "$buildList" | cut -f2 -d'|' | sort -u)

  # echo ${user}':'${batchName}':'${buildList}':'${batchPath}':' len is ${#aLine[@]}

  printf "Updating DB for %s .." "${batchPath}"
  update_build_status -D -d prod:~/.drsBatch.config "$batchPath" FAIL
  rc=$?
  if [[ $rc == "0" ]]; then
    printf "removing path...."
    if [ -d "$batchPath" ]; then
      rm -rf "$batchPath"
    else
      printf " Path %s not found\n" "$batchPath"
    fi
    printf "done\n"
  else
    printf "update_build_status error %s. Not erasing %s\n" $rc $batchPath
  fi
done < <(parseMail.awk $MAIL_TXT | grep -v "${targetErrRE}" $MAIL_DAT | cut -f3,4 -d'|' | sort -u -k1 -t'|')

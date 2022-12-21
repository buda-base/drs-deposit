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
# jimk drs-deposit-108 2022-12-20 ; get literal files out of git
if [[ -z $DB_CONN ]]
then
    printf "FATAL: Cannot connect to database"
    exit 42
fi

function usage() {
  printf "%s\n" "Synopsis: $ME [ -f path_list ] [  -m ]" \
   "    where" \
  "       -f path_list is a file containing a list of batch builds to delete" \
  "       -m is a flag indicating to parse mailerrs.txt" \
  "   both flags can be used"
}
function delete_one() {

  v_batchPath=${1?"delete_one requires a non-null argument."}
  printf "Updating DB for %s .." "${v_batchPath}"
  update_build_status -D -d ${BB_LEVEL:${DB_CONN} "$v_batchPath" FAIL
  rc=$?
  if [[ $rc == "0" ]]; then
    printf "removing path...."
    if [ -d "$v_batchPath" ]; then
      rm -rf "$v_batchPath"
    else
      printf " Path %s not found\n" "$v_batchPath"
    fi
    printf "done\n"
  else
    printf "update_build_status error %s. Not erasing %s\n" $rc $v_batchPath
  fi
}
#

while getopts f:mh opt; do
  # echo "in getopts" $opt $OPTARG
  case $opt in
  f)
    pathList=$OPTARG
    ;;
  m)
    mailFlag=1
    ;;
  h)
    usage
    ;;
  *)
    usage
    ;;
  esac
done

shift $((OPTIND - 1))

if [[ -n $pathList ]]; then
  while read -r build_path <&3; do
    delete_one $build_path
  done 3<$pathList
fi

if [[ -n $mailFlag ]]
then
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

    delete_one "${batchPath}"

  done < <(parseMail.awk $MAIL_TXT | grep -v "${targetErrRE}"  | cut -f3,4 -d'|' | sort -u -k1 -t'|')
fi

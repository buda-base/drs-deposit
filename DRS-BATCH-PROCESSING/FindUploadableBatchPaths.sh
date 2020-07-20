#!/usr/bin/env bash
#
# Creates a list of candidates for depositing to DRS
# Processing:
# 1 . Creates a list of unique volumes in the $PR/batchBuilds folder
# 2.
# Scans the list of batches for duplicat volumes

# From that unique list, it then removes the volumes which have been deposited
# (determined by the global well-known dictionary (see DICT declaration below)
# and then emits the list of directories containing batches which have not been uploaded.
# It's possible that an uploaded batch could contain a volume which has already been uploaded,
# that's an error that HUL DRS detects.
#
# --------     Reads files: ---------------
# DICT (see below) - cumulative dictionary
#
# BuildList:  	output of RemoveDuplicateVolumes.sh - this is the
# pool of volumes which is ready for deposit.
#
# -------------- Writes files -----------------
#
# $DEPOSITED_VOLUMES: from dictionary, volume directories
#
# UnDepositedBuildPaths.txt: Set difference between curDeposits

#
ME=$(basename "$0")
export JUSTNOW=$(date +%H-%M-%S)

[ -z "$BB_LEVEL" ] && {
>&2  echo "${ME}:error: BB_LEVEL not set. Source SetBBLevel.sh"
  exit 1
}

# Filenames
export DICT=/Volumes/DRS_Staging/DRS/KhyungUploads/${BB_LEVEL}/BDRCCumulativeProdDeposits.csv
BATCHES_WITH_DEPOSIT=$(mktemp -p . --suffix=.lst batchesWithADeposit-$JUSTNOW-XXX)
UNIQUE_VOLUMES=$(mktemp -p. --suffix=.lst UNIQUE-VOLUMES-${JUSTNOW}-XXXX)
UNDEPOSITED_VOLUME_PATHS=$(mktemp -p. --suffix=.lst UNDEPOSITED_VOLUME_PATHS-${JUSTNOW}-XXXX)
DEPOSITED_VOLUMES=$(mktemp -p . --suffix=.lst volsInDRSDeposit-${JUSTNOW}-XXXX)
COUNTFILES_AWK=~/bin/CountFilesInBatches.awk

>&2 echo $(date)
#
# Get the unique volumes
#  Thanks SO for clever way to sort by last field:
# awk -F'/' '{print $NF,$0}' | sort | cut -f2 -d' ' |
# Sort on the last field, reassemble the full paths.
# Then, scan each line, printing where the last field is different from the saved last field.
# Sort on the last field, reassemble the full paths.
# Then, scan each line, printing where the last field is different from tBTW, you should know thathe saved last field.
# This line may have been causing problems with not finding batchBuilds
for riji in $(find $PR/batchBuilds -maxdepth 3 -name batch.xml); do find $(dirname $riji) -maxdepth 1 -mindepth 1 -type d; done |
  awk -F'/' '{print $NF,$0}' | sort | cut -f2 -d' ' |
  awk -F/ 'BEGIN {vol="CANTFIND"; rmDups = "foundDuplicateVolumes.lst" } { if ($NF != vol)  { print $0 ; vol = $NF }else {print $0 > rmDups  } } ' \
    >$UNIQUE_VOLUMES

>&2  echo  $(date +%H-%M-%S)  $(ls -l "$UNIQUE_VOLUMES")
#
# 2. Get the lis of deposited volumes from the master dictionary
#
# You may ask: why not just look for a batch directory:
# Because the batch directories may have different roots, or a
# volume may have been built in several batch directories.
#
# Heuristic. Here's a known volume build. find its column index
# in the dictionary
# This OSN is known to exist in both Prod and QA
export PROBE=W1GS66344-I1GS66346
#
for idx in $(seq 1 25); do
  test=$(awk -F',' -v fNum="$idx" -v searchTarget=$PROBE '{ if ($fNum == searchTarget) {print fNum}}' $DICT)
  [[ -n "$test" ]] && break
done
result=$(printf "Found volume %s in comma separated field %s\n" $PROBE "$idx")
>&2 echo  $(date +%H-%M-%S)  "$result"

#
# Could use grep, but I want the field separation syntax to be the same,
# sometimes there are commas in quoted fields



awk -F',' -v volumeField="$idx" '{print $volumeField }' $DICT | sort -u  >"$DEPOSITED_VOLUMES"

>&2 echo  $(date +%H-%M-%S)  $(ls -l "$DEPOSITED_VOLUMES")

# 3. Remove the list of deposited volumes from the total list
# This line only removed the specific lines. It leaves in batches where the line appeared.
# grep -w -v -f $DEPOSITED_VOLUMES  $UNIQUE_VOLUMES | sort -u > $outFile
# Change so that it gets all the batch directories which contain one or volumes which are in dict.
#
grep -w -f "$DEPOSITED_VOLUMES" "$UNIQUE_VOLUMES" | xargs -n 1 dirname | sort -u  | xargs -n1 basename  >"$BATCHES_WITH_DEPOSIT"

>&2 echo  $(date +%H-%M-%S)  $(ls -l "$BATCHES_WITH_DEPOSIT")

# Now scan the volume list to remove those batches tht have been deposited
# if there are no deposited batches, just copy the volume list
# (because grep -v -f empty file produces no output
#
# Then process out the volume names to get the parent folders (xargs -n1 dirname | sort -u)
#
if [[ ! -s "$BATCHES_WITH_DEPOSIT" ]]; then
  cat "$UNIQUE_VOLUMES"  | xargs -n1 dirname | sort -u  >"$UNDEPOSITED_VOLUME_PATHS"
else
  grep -w -v -f "$BATCHES_WITH_DEPOSIT" "$UNIQUE_VOLUMES" | xargs -n1 dirname  | sort -u  >"$UNDEPOSITED_VOLUME_PATHS"
fi


>&2 echo $(date +%H-%M-%S) $(ls -l "$UNDEPOSITED_VOLUME_PATHS")

# 4. From those undeposited volumes, cat out the first 200, which is usually more than the
# DRS system can ingest in a day anyway.
#
head -200  "$UNDEPOSITED_VOLUME_PATHS" | awk '{ \
    cmd = "find "$1" -type f | wc -l" ; \
    cmd | getline thisCount ; \
     close(cmd); \
     sumCount += thisCount;print $1 "|" thisCount "|" sumCount; \
      }'

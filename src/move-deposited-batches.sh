#!/usr/bin/env bash
# Move deposited batches to $PR/deposited-batch-builds

export SRC=$PR/batchBuilds
export TARGET="$PR/deposited-batch-builds"
[[ -d $TARGET ]] || mkdir -p "$TARGET"
export DICT=/Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCumulativeProdDeposits.csv
# head -20 $DICT | grep batchW |  awk -F, '{ split($12,dt,"T"); print($10, dt[1])}' |  sort -u | head -1 | parallel --colsep ' ' 'mkdir -p $TARGET/{2} && mv -v $SRC/{1} $TARGET/{2}'
cat $DICT | grep batchW | awk -F, '{ split($12,dt,"T"); print($10, dt[1])}' | sort -u | parallel --jobs 6 --joblog mv.log --colsep ' ' 'if [[ -d $SRC/{1} ]] ; then mkdir -p $TARGET/{2} ; mv -v $SRC/{1} $TARGET/{2} ; else echo {1} not found ; fi | tee -a {%}.run.log'

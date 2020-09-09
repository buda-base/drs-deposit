#!/usr/bin/env bash
#
#
# Get a list of all builds
PATH_ALL_BUILD=all-build-path.lst
BUILD_WITH_DUP_VOLS=dup-vol-path.lst
VOLS_NOT_DEP=volumes-not-deposited

function dtf()  {
    echo -n $(date +%M.%S)
    }


printf "%s get built volumes..." $(dtf)
find ${PR}/batchBuilds  -maxdepth 2 -mindepth 2 -type d | grep batchW  > $PATH_ALL_BUILD
printf "Done\n%s Extract duplicate volumes, and their build paths...." $(dtf) 
awk -F'/' '{print $8}' $PATH_ALL_BUILD  | sort | uniq -d | grep -F -f - $PATH_ALL_BUILD > .tmp
     cat .tmp | xargs dirname | sort -u   >   $BUILD_WITH_DUP_VOLS

#Read the list of duplicate builds
# Get the build directories of the duplicate volumes. Put them into one file for each build
while read dupb ; do ls  $dupb >  $(basename ${dupb}).dup-build.lst  ; done < $BUILD_WITH_DUP_VOLS

printf "Done\n%sGet the OSN (volume label) and batch of the deposited..." $(dtf)
# Find outhow may of the duplicate builds have been deposited. Cut the list for something we can use in the DRS database.
cat *.dup-build.lst | sort -u | grep -F -f - /Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCumulativeProdDeposits.csv | cut -f2,10 -d, >  final-results.lst
printf "Done\n%s Calc volumes not deposited..." $(dtf)
#
# Now, we need to get all the undeposited volumes out of builds which contain deposited volumes
cut -f1 -d, final-results.lst | grep -F -v -f - *dup-build.lst | grep -v 'batch.xml' | sed 's/\.dup-build\.lst:/,/' | tee $VOLS_NOT_DEP
printf "Done\n%s See $VOLS_NOT_DEP  Double check....\n"

#
# Double check
cut -f2 -d, vols-not-deposited | grep -F -f - /Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCumulativeProdDeposits.csv
printf "Done. No output means success\n"

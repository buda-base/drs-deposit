#! /bin/bash -vx
#                        Input list (W,Holis pairs)     
 # Really using this: DEST_PATH="/Volumes/DRS_Staging/StagingBatchProject`date +%F.%H.%M`"
 #
 # This is for testing ftp cycles
 DEST_PATH=/Volumes/DRS_Staging/StagingBatchProject2017-12-11.14.18
 #
 # jsk: this is WebArchive onRS3. Depends on the script host having mounted it.
 WORKS_HOME=/Volumes/WebArchive
 DRS_HOME=/Users/jimk/svn/DRS-BATCH-PROCESSING

 export DRS_HOME
[ -e "$1" ] || { echo "$(basename $0)": WorksList \'"$1"\' must exist but does not ; exit 2; }
${DRS_HOME}/make-drs-batch-pos-indep.sh "$1" ${DRS_HOME}/BB_tbrc/BB_tbrc2drs  $DEST_PATH  $WORKS_HOME /Users/jimk/DRS/BatchBuilder-2.2.11



















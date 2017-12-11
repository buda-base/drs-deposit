#!/bin/bash -x

DEFAULT_BATCH_DIR_PATTERN="batchW*"
BATCH_DIR_PATTERN=$DEFAULT_BATCH_DIR_PATTERN
BATCH_XML=batch.xml
WAIT_SUFFIX=".wait"

ME=$(basename $0)
[ "x$1" == "x" ] && { printf "Usage: ${ME} sourceRoot [opt: batchDirPattern ]  where  \
\n\t sourceRoot is the parent directory of batches to be uploaded \
\n\t batchDirPattern is the prefix of subdirectory names of sourceRoot which contain batches \
\n\t\t default batchDirPattern is 'batchW*'\n"; 
  } 

[ -d "$1" ] || { echo "${ME}: sourceRoot "$1" is not a directory or does not exist" ; exit 2 ;  } 

# override default batch dir pattern
[ "x$2" ==  "x" ] ||  BATCH_DIR_PATTERN=$2 ;

# For each batch

BATCH_ROOT=${1}$BATCH_DIR_PATTERN

for b in ${BATCH_ROOT} ; do # rm /* it goes one level too deep
	bTarget=$(basename $b)
	 [ -f $b/$BATCH_XML ] && mv $b/$BATCH_XML $b/${BATCH_XML}${WAIT_SUFFIX}
	 sftp -o LogLevel=ERROR -P 15366 -i /Users/jimk/ppk/rootAtWeyrSSH.ppk jimk@inner.tbrc.org:incoming/ << FRELM 2> ftp.log
	 mkdir $bTarget
	 # you have to make the directory, and then put stuff in it. here,
	 # $bTarget must be the last directory in the path $b 
	 put -r $b 
	 # operations are relative to the directory in the command line ":incoming"
	 rename ${bTarget}/${BATCH_XML}${WAIT_SUFFIX} ${bTarget}/$BATCH_XML
FRELM
done

# ssh -p 15366 -i /Users/jimk/ppk/rootAtWeyrSSH.ppk -l jimk inner.tbrc.org << FRELM
# cd tmpRm
# ./start-loading.sh
# FRELM





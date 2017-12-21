#!/bin/bash
#
###

ME=$(basename $0)

usage() {
	 printf "\b\nUsage: ${ME} sourceRoot [opt: batchDirPattern ]  where  \
\n\t sourceRoot\t\tis the parent directory of batches to be uploaded \
\n\t batchDirPattern\toverrides the default prefix of subdirectory names \
\n\t\t\t\tof sourceRoot which contain batches.\
\n\t\t\t\tdefault prefix is 'batchW*'\n\n"; 
exit 1;
}

# do we have what we need?
[ "x$1" == "x" ] && usage


DEFAULT_BATCH_DIR_PATTERN="batchW*"
BATCH_DIR_PATTERN=$DEFAULT_BATCH_DIR_PATTERN
BATCH_XML=batch.xml
WAIT_SUFFIX=".wait"

#section error logging. Requires trailing /
set -vx
. ./setupErrorlog.sh "${ME}"
#endsection error logging
set +vx
read -p "${ERR_LOG}"

[ -d "$1" ] || { echo "${ME}: sourceRoot "$1" is not a directory or does not exist" ; exit 2 ;  } 

# override default batch dir pattern
[ "x$2" ==  "x" ] ||  BATCH_DIR_PATTERN=$2 ;

# For each batch

BATCH_ROOT=${1}$BATCH_DIR_PATTERN   

for b in ${BATCH_ROOT} ; do # rm /* it goes one level too deep
	bTarget=$(basename $b)
	 [ -f $b/$BATCH_XML ] && 
	 {
	     mv $b/${BATCH_XML}NOPE $b/${BATCH_XML}${WAIT_SUFFIX} 
		 rc=$?;
	
	     [ $rc == "0" ] || 
	     {
		 	errstr="${ME}: error: ${b} batch xml rename failed.  $rc";
		 	echo $errstr ;
		 	echo $errstr >> $ERR_LOG ; 
		 	# exit $rc; 
	     }
	 }
done

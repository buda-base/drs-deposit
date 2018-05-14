#!/bin/bash
#
# Enclose BuildRecoveryList.awk


export ME=$(basename $0)
export MEDIR=$(dirname $0)

. $MEDIR/setupErrorLog.sh

function usage() {
	cat << USAGE
	    synopsis: BuildDeepDeleteList -h  this message
        synopsis: BuildDeepDeleteList  -o outdir -p prefix -s srcs datafile

        where:
                -o      is the destination directory for sets of sftp scripts
                -p      is the prefix for sftp scripts
                -s      ARG_SRCS is the filespec for a set of files which is 
                		contains paths to built.cMetachars must be quoted 
                		(e.g. 'frelm*.txt')
                dataFile is a list of batch names, one per line.

USAGE
}

while getopts o:p:s:h opt ; do
	# echo "in getopts" $opt $OPTARG
	case $opt in
		o)
			oArg=$OPTARG;
			;;
		p)
			pArg=$OPTARG
			;;
		s)
			sArg=$OPTARG
			;;
		h)
			usage
			exit 0
			;;
	esac
done

shift $((OPTIND-1))


outdir=${oArg?${ERROR_TXT}:destination directory required. See ${ME} -h}
prefix=${pArg?${ERROR_TXT}:prefix required. See ${ME} -h }
srcList=${sArg?${ERROR_TXT}:sources required. See ${ME} -h }

# Let awk parse
BuildDeepDeleteList.awk -v ARG_SRCS=$srcList -v ARG_OUTDIR=$outdir  -v ARG_PREFIX=$prefix $1

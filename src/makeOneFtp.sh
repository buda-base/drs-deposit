#! /bin/bash
#   Make one Ftp Launch, with tracking control
#
# arguments:

#
# Major mods:
# jimk 2020-10-09: removed status and completion monitoring flder roots: using gnu parallel instead
function Usage {
cat << ENDUSAGE
synopsis:
${ME}  batchDirPath remoteUserName

batchDirPath: 		Path to a file containing a list of folders to upload

remoteUserName		credential for remote system

remotePath		(optional) remote host name (for QA)
ENDUSAGE
}


# Some constants
FTPSCRIPT='ftpScript.sh'

ME=$(basename "$0" )

if (( $# <  2)) || (( $# > 3)) ; then
  echo nargs: $#
  echo args  "$@"
Usage
exit 1;
fi

[ -f "$1" ] || { echo "${ME}":error: source list  \'"$1"\' must exist but does not. ; exit 2; }
srcListPath=$1
srcListName=$(basename "$1" )

remoteUserName=${2?${ME}:error: remote User Name not given}

remoteHost=$3

# Invoke the upload in the background


# jimk: with parallel, we dont need this overhead
${FTPSCRIPT} $srcListPath $remoteUserName $remoteHost

exit


#!/bin/bash
ME=$(basename $0)

usage() {
	cat << USAGE

	Usage: splitWorks.sh worksList where
		worksList		is the list of works to be batched.
	Setup:
	 	default is to write 240 lines / worksList. Change it by editing this
	file
USAGE
exit 1;
}

declare -i worksPerRun
worksPerRun=3 
# do we have what we need?
[ "x$1" == "x" ]  && usage

sourceFile=$1

[ -f $sourceFile ] || { echo "${ME}: source file \"$sourceFile\" does not exist or is not a file." ; exit 2 ; }

#
# worksList fileName
worksFn=${2:-worksList}


#
declare -i fileCount
fileCount=0

declare -i fileIndex
fileIndex=0

while IFS=',' read -ra  workLine ; do
	# This allows csv files to have their lines copied.
	# Could have just copied the raw line....
	# doublequoted "${x[*]}" shows IFS separated list of array elements
	IFS=',' # while's IFS setting is ex scope
	echo "${workLine[*]}"  >> ${worksFn}${fileCount}.txt
	[ $fileIndex  == 0 ]  && echo "Creating file ${fileCount}"
		((fileIndex++))
	[ $fileIndex  == ${worksPerRun} ]  && ((fileCount++))
	[ $fileIndex  == ${worksPerRun} ]  && fileIndex=0

done < $sourceFile

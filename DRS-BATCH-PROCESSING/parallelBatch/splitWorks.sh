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
worksPerRun=240
# do we have what we need?
[ "x$1" == "x" ] && usage


sourceFile=$1

[ -f $sourceFile ] || { echo "${ME}: source file \"$sourceFile\" does not exist or is not a file." ; exit 2 ; }



#
declare -i fileCount
fileCount=0

declare -i fileIndex
fileIndex=0

while IFS=',' read -ra  workLine; do
	echo ${workLine[0]},${workLine[1]},${workLine[2]}   >> worksList${fileCount}.txt
	[ $fileIndex  == 0 ]  && echo "Creating file ${fileCount}"
		((fileIndex++))
	[ $fileIndex  == ${worksPerRun} ]  && ((fileCount++))
	[ $fileIndex  == ${worksPerRun} ]  && fileIndex=0

done < $sourceFile

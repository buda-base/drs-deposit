#!/bin/bash
ME=$(basename $0)

usage() {
	 printf "\b\nUsage: ${ME} worksList  where  \
\n\t worksList\t\tis the list of works to be batched.\n" ; 
exit 1;
}

# do we have what we need?
[ "x$1" == "x" ] && usage


sourceFile=$1

[ -f $sourceFile ] || { echo "${ME}: source file \"$sourceFile\" does not exist or is not a file." ; exit 2 ; }


declare -i worksPerRun
worksPerRun=240
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

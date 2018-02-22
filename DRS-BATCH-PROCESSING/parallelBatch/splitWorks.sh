#!/bin/bash -vx
ME=$(basename $0)

usage() {
	cat << USAGE

	Usage: splitWorks.sh [OPTIONS] worksList 
	OPTIONS:
		-l (length)	split the source into files of 'n' length. (default)
		-w (width)  split the source into 'n' files, of as close to equal length as possible
		-n 				number of files/lines (default is 4)
		-p (prefix)		Prefix of output file names (default worksList)
		-h (help)		Shows this message
		worksList		is a file containing lines of text which get put into output files

	splitWorks.sh splits worksList into files in the current directory.
	The files retain the extension of the original file


USAGE
exit 1;
}

declare -i worksPerRun
unitsPerList=3 

declare HFLAG="h"
declare VFLAG="v"
declare direction=$HFLAG
direction=
# do we have what we need?

while getopts n:hlwp: opt ; do
	case $opt in
		l)
			direction=$HFLAG;
			;;
		w)
			direction=$VFLAG;
			;;
		n)
			unitsPerList=$OPTARG ;
			;;
		p)
			worksFn=$OPTARG ;
			;;
		h)

	esac
done

shift $((OPTIND-1))
echo "whats left :${@}:"
[ "x$1" == "x" ]  && usage

sourceFile=$1

[ -f $sourceFile ] || { echo "${ME}: source file \"$sourceFile\" does not exist or is not a file." ; exit 2 ; }

#
# Give worksFn a default, if none
srcBase=$(basename $sourceFile)
# Take only the first segment with %%
worksFn=${worksFn:-${srcBase%%.*}}"."

#
# if VFLAG, we want a certain number of files.

fileCount=$(($(wc -l < $sourceFile)))
#
# If creating a specific number of files, adjust the lines per file
if [ "$direction" == "$VFLAG" ] ; then
	#
	# Allow for remainder
	linesPerFile=$(( 1 + $fileCount/$unitsPerList))
	read -p "lpf?"
else
	linesPerFile=$(($unitsPerList))
fi

#
# HACK alert: convert base 10 to base 26
suffixLen=$(($(echo $((($fileCount/$linesPerFile)+1)) | awk '{print int(log($1)/log(26)) + 1}')))


read -p "$suffixLen :"  # "$(printf "direction=%s unitsPerList=%s file=%s" $direction $unitsPerList  $worksList )"

#
# This is BSD split. If we move to Ubuntu, look up GNU
split -l $linesPerFile -a $suffixLen $sourceFile $worksFn

exit $!
# while IFS=',' read -ra  workLine ; do
# 	# This allows csv files to have their lines copied.
# 	# Could have just copied the raw line....
# 	# doublequoted "${x[*]}" shows IFS separated list of array elements
# 	IFS=',' # while's IFS setting is ex scope

# 	if [ $direction == $HFLAG ]  ; then 
# 		echo "${workLine[*]}"  >> ${worksFn}${fileCount}.txt
# 		[ $fileIndex  == 0 ]  && echo "Creating file ${fileCount}"	
# 	else	
# 		echo "${workLine[*]}"  >> ${worksFn}${fileIndex}.txt
# 		[ $fileIndex  == 0 ]  && echo "Wrapping back to file ${fileIndex}"		
# 	fi

# 	((fileIndex++))
# 	[ $fileIndex  == ${unitsPerList} ]  && ((fileCount++))
# 	[ $fileIndex  == ${unitsPerList} ]  && fileIndex=0

# done < $sourceFile

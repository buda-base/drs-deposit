#!/bin/bash
ME=$(basename $0)

usage() {
	cat << USAGE

	Usage: splitWorks.sh [OPTIONS] worksList 
	OPTIONS:
		-l n 	split the source into files of 'n' length. (default)
		-f n 	split the source into 'n' files, of as close to equal length
				as possible
		-p prefix		Prefix of output file names (default same as base of 
						worksList. Risky.)
		-h (help)		Shows this message
		worksList		is a file containing lines of text which get split
						into output files

	The files retain the extension of the original file, if any, ".txt" if none
USAGE
exit 1;
}

declare -i worksPerRun
unitsPerList=3 

declare LFLAG="l"
declare FFLAG="f"

# do we have what we need?

while getopts l:f:p:h opt ; do
	case $opt in
		l)
			direction=$LFLAG;
			unitsPerList=$OPTARG ;
			;;
		f)
			direction=$FFLAG;
			unitsPerList=$OPTARG ;
			;;
		p)
			worksFn=$OPTARG ;
			;;
		h)
			usage;
			exit 1;
			;;
	esac
done

shift $((OPTIND-1))

: ${1?${ME}:error: worksList is not given. See ${ME} -h}

: ${direction?${ME}:error: -l n or -f n is required.}

if (($unitsPerList <= 0)) ; then 
	echo "${ME}:error n = ${unitsPerList}. n must be a positive integer" ;
	exit 1;
fi


sourceFile=$1

[ -f $sourceFile ] || { echo "${ME}: source file \"$sourceFile\" does not exist or is not a file." ; exit 2 ; }

#
# Give worksFn a default, if none
srcBase=$(basename $sourceFile)
# Take only the first segment with %%
worksFn=${worksFn:-${srcBase%%.*}}"."

fileCount=$(($(wc -l < $sourceFile)))
#
# If creating a specific number of files, adjust the lines per file
case $direction in
	${FFLAG})
	# Was getting wrong results when (All lines MOD lines/file)  == 0
	# Eg splitting a file of 12 lines into 4 files.
	adjuster=$((0))
	if [ $(($fileCount % $unitsPerList)) != 0 ] ; then
		adjuster=$((1))
	fi

	linesPerFile=$(( $adjuster + ($fileCount/$unitsPerList)))
	;;

	${LFLAG})
	linesPerFile=$(($unitsPerList))
	;;
esac


#
# This is BSD split. If we move to Ubuntu, look up GNU

split -l $linesPerFile $sourceFile $worksFn # -a $suffixLen 

rc=$(($!))

 [ ! $rc ]  && { echo "${ME}:error: ${rc}" ; exit $rc ; }

i=$((0))
for file in ${worksFn}*
do
    # ${file/%.*/mumble} means replace the pattern that starts at end of string
    mv "$file" "${file/%.*/$((++i)).txt}"
done

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

#! /bin/bash

# script to collect imagegroups into a batch for processing via BatchBuilder and
# upload to Harvard Digital Repository Service
#
# this script is called as follows:
#
#     make-drs-batch.sh workVolumes projectMaster targetProject archiveDir bbDir
#
# the arguments are:
#
#		workList		is the path to a text file each line of which is a tuple of
#                                TBRC RID, Hollis ID, Volume, OutlineOSN, and PrintMasterOSN
#						the Hollis ID is retrieved from the ingest of the TBRC Work records
#						via the MARC service. The Hollis ID is used to retrieve the MODS
#						metadata for each Volume (PDS object) of the Work given by the RID
#
#		projectMaster	is the path to a BatchBuilder project that has been initialized via
#						the BathBuilder GUI. This should include the project level defaults
#						such as various login ids and other codes. The project should also
#						have the default Object Template set up - see the skeleton project in
#						the SVN TBRCTools/scripts Cloudforge project
#
#		targetProject	is the name of the project that will contain the generated batches
#
#		archiveDir		is the path to the image archive from which the imagegroups are 
#						retrieved
#
#		bbDir			this is the path to the directory containing batchbuildercli.sh and
#						supporting files - i.e., the BatchBuilder install. See the harvard-drs
#						SVN in TBRCTools/scripts or visit:
#
#							http://hul.harvard.edu/ois/systems/drs/drs2-software.html
#
# Processing:
# After some setup of source and targets, this script's main processing loop:
#   - Reads each line of the input file, and parses it into
#   -   Work
#   -   HOLLIS
#   -   Volume
#   -   PrintMasterOSN
#   -   OutlineOSN
# It is assumed that the Work, Volume, PrintMasterOSN, and OutlineOSN
# This script copies and renames the images in each imagegroup of each Work listed in the
# worksList. The images are copied into the project/template/image directory.
#
# Then the batchbuildercli.sh is called to create the batch directory structure in the 
# project directory. After this, the batchbuildercli.sh is called again to create the control
# files: batch.xml and descriptor.xml which are used to control the DRS import.
#
# The approach is to copy the projectMaster to make a new project that will contain a batch for
# for each Work to be deposited.
#
# For each batch / Work need to run saxon to prepare the project.conf file
# with the Hollis ID for the Work - this is in lieu of generating a really
# long command line. The saxon needs to be run like:
#
#    java -jar saxonhe-9.4.0.7.jar the-project.conf make-proj-conf.xsl hId=the-hollis-id
#

# jsk 12.21.17 ##https://github.com/BuddhistDigitalResourceCenter/drs-deposit/issues/14
# Filter out banned extensions
declare -a BANNED_EXT=('tmp' 'png' 'pdf' 'db' 'DS_Store' )


function toLower() {
	echo $1 | tr '[:upper:]' '[:lower:]'
}
#
# return true (0) if an extension is banned
function isBannedExt() {
	testExt=$(toLower "$1")
	for anExt in ${BANNED_EXT[@]} ; do
		[ "$testExt" == "$(toLower $anExt)"  ] && return 0;
    done
	return 1 
}
#
# copy logs for this bath builder run,
# and remove them

function cleanUpLogs() {
	  # jimk 21.I.18: copy batchbuilder log
	  batchLogDir=$targetProjectDir/${1}"-"logs
        mkdir $batchLogDir
        # Keep al the logs for reference, but extract into a summary
        cp -R $bbLogDir $batchLogDir
        cp $logPath $batchLogDir
        rm -rf $bbLogDir
        rm -rf $logPath
        # Summarize and extract
        # jsk: issue #44: wasn't finding errors correctly. 
        # find ... -name -o xyz -o -name abc doesn't look for abc when it finds abc
        find $batchLogDir -type f -not -name errorSummary.txt -exec grep -H -n -i 'err\|warn\|except' {} \; \
        >> ${batchLogDir}/errorSummary.txt
}

#
# function trailingNums
# returns the integer defined by the last 'n' digits of a string
#
# Args:
# $1...$n-1 testString (can contain spaces)
# $@ maxLength: max length to parse
#
# loop L from maxLength to 1 until the last L characters form a numeric
#
# Returns empty string if args are empty, invalid (i.e. maxLength > length of string)
# or testString does not end with a numeric. (i.e. should fail trailingNumbs "fr3d" 2)

function trailingNums() {
	# the arg length
	wordsInArgs=$(($#-1))
	array=${@:1:$wordsInArgs}

	for s in ${array} ; do
		testString=$(printf " %s %s" $testString $s)
	done
	#Strip trailing
	testString=${testString%${testString##*[![:space:]]}}
	#
	# last arg
	maxLength="${!#}" 
	# Anything?
	[ -z "$testString"  ]  && return
	# maxLength must be positive integer
	# // strips out all the numerics, -n tests the remainder for anything left
	# if there was anything, it's not a sequence of digits
	[ -z "${maxLength//[0-9]}" ] && [ -n "$maxLength" ] || return
	[ $maxLength -le 0 ] && return

	# invert maxlength, to get end of string
	result=""
	maxLength=-$maxLength

	while [ -z "$result" -a $maxLength -lt 0 ] ; do
		testNum=${testString: maxLength}
		#
		# See above
		[ -z "${testNum//[0-9]}" ] && [ -n "$testNum" ] || { 
			d=$((maxLength++))
			continue
		}
	echo $testNum
	return
done
return
}


TIMING_LOG_FILE=timeBuildBatch.log
# bash builtin time format
TIMEFORMAT=$'%R\t%U\t%S\t%P'
export TIMEFORMAT

# Who's running?
ME=`basename ${0}`

if [ "$#" -ne 5 ]; then
	echo "${ME}: Needs 5 parameters"
	echo "Usage: make-drs-batch worksList projectMaster targetProjectDir archiveDir bbDir"
	exit 1
fi

# jsk: need full path to script for components
 MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

worksList=$1
echo Works List File: $worksList
if [ ! -f $worksList ]; then
	echo "${ME}: worksList \'${1}\' does not exist or is not a directory"
	exit 2
fi

projectMaster=$2
echo BB Project Directory: $projectMaster
if [ ! -d $projectMaster ]; then
	echo "${ME}: projectMaster \'${2}\' does not exist or is not a directory"
	exit 2
fi
masterProjConf=$projectMaster/project.conf

archiveDir=$4
echo Archive Directory: $archiveDir
if [ ! -d $archiveDir ]; then
	echo "${ME}: archiveDir \'${4}\' does not exist or is not a directory"
	exit 2
fi

bbDir=$5
bb=batchbuildercli.sh

echo BB: $bbDir $bb
if [ ! -d $bbDir ]; then
	echo "${ME}: BatchBuilder directory  \'${5}\' does not exist or is not a directory"
	exit 2
fi
if [ ! -f $bbDir/$bb ]; then
	echo "${ME}: batchbuildercli.sh does not exist in $bbDir"
	exit 2
fi
bb=${bbDir}/$bb
# jimk 24.1.18: copy  batchbuilder logs, including failed files
bbLogDir=${bbDir}/logs


# jsk: Target project might be absolute
targetProjectDir=$3

# template dir path suffix (template/image) is defined in the project conf. If changed there,
# must be changed here.
templateDir=$targetProjectDir/template/image

logPath=$targetProjectDir/bb-console.txt

echo Target Project Directory: $targetProjectDir

if [ -e $targetProjectDir ]; then
	echo "${ME}: targetProjectDir ${targetProjectDir} already exists. Remove it or use a different name"
	exit 2
fi
mkdir "$targetProjectDir"

echo targetProjectDir: $targetProjectDir  >> $logPath 2>&1
# 
# Start timing log

# create a BB project to hold the batches that will be created
# jsk 11/7/17: create this structure
# bb has to be defined before this works
#
# jsk 12/5/17: don't need to create this anymore. The folders 
# are created in the templatedirs BB action, and the 
# project.conf is written by doing an xsl transform on the master
#
# echo Create target dir cp -R $projectMaster $targetProjectDir
# echo cp -R $projectMaster/* $targetProjectDir  >> $logPath 2>&1
# cp -Rp $projectMaster/* $targetProjectDir  >> $logPath 2>&1
# You do nees to copy something
cp $masterProjConf $targetProjectDir >> $logPath 2>&1

# Fill in the template

echo $bb -a templatedirs -p $targetProjectDir
echo $bb -a templatedirs -p $targetProjectDir  >> $logPath 2>&1
$bb -a templatedirs -p $targetProjectDir>> $logPath 2>&1

targetConf="$targetProjectDir/project.conf"

# 30 is about 18 - 20000 files, which is too
# many for poor old DRS.
volsPerBatch=20
echo Volumes per Batch: $volsPerBatch

echo Template Image Directory: $templateDir

echo Works List File: $worksList >> $logPath 2>&1
echo BB Project Directory: $projectMaster >> $logPath 2>&1
echo Target Project Name: $targetProjectDir >> $logPath 2>&1
echo Archive Directory: $archiveDir >> $logPath 2>&1
echo Template Image Directory: $templateDir >> $logPath 2>&1
echo Volumes per Batch: $volsPerBatch >> $logPath 2>&1

while IFS=',' read -ra LINE; do
	RID=${LINE[0]}
	HID=${LINE[1]}
	echo TBRC $RID at HOLLIS $HID
	echo TBRC $RID at HOLLIS $HID >> $logPath 2>&1
	#
	# jsk Pos indep 12/7/17
	# cd $workingDir
	# make a custom project.conf for the current work.
	# jsk 12/5/17: Sketchy, because it writes
	# project.conf with the HOLLIS number after every build.
	# Look into using property arguments to bb
	java -jar "${MEPATH}/saxonhe-9.4.0.7.jar" $masterProjConf ${MEPATH}/make-proj-conf.xsl hId=$HID > $targetConf


	imagesDir=$archiveDir/$RID/images
	batchNameBase="batch$RID"
	echo Batch Name base: $batchName
	echo Images Directory: $imagesDir
	echo Images Directory: $imagesDir >> $logPath 2>&1
	
	declare -a volNms=($imagesDir/*)
	numVols=${#volNms[@]}
	numBatches=$(((numVols + volsPerBatch - 1) / volsPerBatch))
	
	start=0
	for part in $(seq 1 ${numBatches%.*}) ; do
		# create a batch for the current slice of the array of volumes
		for v in ${volNms[@]:start:volsPerBatch} ; do
			# for each volume in the slice cp and rename the images
			echo ImageGroup Directory: $v
			echo ImageGroup Directory: $v >> $logPath 2>&1
			pdsName=$(basename $v)
			
			
			for f in $v/* ; do
			# cp and rename each image
				fullNm=$(basename $f)
				ext="${fullNm##*.}"

				# jsk: 12.21.17: Issue #14
				 if $(isBannedExt ${ext} ) ; then continue ; fi
				fnm="${fullNm%.$ext}"

				# jsk 01Feb18: Issue #33. Note this requires the filename to end in 4 digits
				# dont use page seq - suffix=$(printf %04d $pageSeq)
				#
				# TrailingNums returns a string of numerics, not a real integer
				suffix=$(trailingNums ${fnm} 4)

				[ "$suffix" == "0" -o -z "$suffix" ] && { 
						echo ${ME}:ERROR: Invalid sequence in file $fnm
						echo ${ME}:ERROR: Invalid sequence in file $fnm >> $logPath 2>&1
					continue
				}

				# This transform makes the file name comply with PDS sequencing
				destNm="$pdsName--${fnm}__${suffix}.$ext"			
				cp $f $templateDir/$destNm			
			done
		done

		batchName="$batchNameBase-$part"
	# jsk: already prepended bb with the bb path.
		# cd $bbDir

		echo $bb -a buildtemplate -p $targetProjectDir -b $batchName
		echo $bb -a buildtemplate -p $targetProjectDir -b $batchName >> $logPath 2>&1
	    $bb -a buildtemplate -p $targetProjectDir -b $batchName >> $logPath 2>&1

		# Count files in batch
		# nFiles=`find $targetProjectDir -type f | wc -l`
		# echo -n ${batchName} nFiles  $nFiles ' ' >> $TIMING_LOG_FILE
		
		echo $bb -a build -p $targetProjectDir -b $batchName
		echo $bb -a build -p $targetProjectDir -b $batchName >> $logPath 2>&1
        
        # { time $bb -a build -p $targetProjectDir -b $batchName >> $logPath 2>&1 ; } 2>> $TIMING_LOG_FILE
        $bb -a build -p $targetProjectDir -b $batchName >> $logPath 2>&1

		# jsk 11.dec.17. Dont rename here. Do it in ftp script
		# if [ -f $targetProjectDir/$batchName/batch.xml ]; then
		# 	mv $targetProjectDirbatchName/batch.xml $targetProjectDir/$batchName/batch.xml.wait
		# else
		# 	echo BB failed for $batchName
		# 	echo BB failed for $batchName >> $logPath 2>&1
		# fi
		if [ -f $targetProjectDir/$batchName/batch.xml ] ; then

			echo ${ME}:ERROR:BB failed for $batchName ;
			echo ${ME}:ERROR:BB failed for $batchName >> $logPath 2>&1 ; 

			# We could decide to continue 
			# exit 1;
		else
		    # set up mets
		    td=$(mktemp -d)
		    tojsondimensions.py -i $targetProjectDir/$batchName -o $td 2>&1 | tee -a $logPath
		    rm $td  2>&1 | tee -a ${logPath}
		fi

        # jimk 2018-V-18: this used to be above the last fail.
       cleanUpLogs $batchName

		start=$[start + volsPerBatch]
	done
done < $worksList

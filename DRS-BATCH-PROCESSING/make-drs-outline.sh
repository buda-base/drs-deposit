#!/bin/bash

# script to collect transformed outlines into a batch for processing via BatchBuilder and
# upload to Harvard Digital Repository Service
#
# this script is called as follows:
#
#     make-drs-outline.sh worksList projectMaster targetProject archiveDir bbDir
#
# the arguments are:
#
#		worksList		is a text file each line of which is a pair of TBRC RID,Hollis ID
#						(the Hollis ID is retrieved from the ingest of the TBRC Work records
#						via the MARC service. The Hollis ID is used to retrieve the MODS
#						metadata for each Volume (PDS object) of the Work given by the RID)
#						Finding the worklist is done out of band.
#
#		projectMaster	is the path to a BatchBuilder project that has been initialized via
#						the BathBuilder GUI. This should include the project level defaults
#						such as various
# login ids and other codes. The project should also
#						have the default Object Template set up - see the skeleton project in
#						the Github drs-deposit/BB_tbrcBB_tbrc2drs
#
#		targetProjectDir	is the name of the project that will contain the generated batches
#
#		outlineSrcRoot	is the path to the outline archive from which this script retrieves
#						the outlines. This archive is only folders, named after first two characters
#						of the MD5 has of the works they contain
#
#		bbDir			this is the path to the directory containing batchbuildercli.sh and
#						supporting files - i.e., the BatchBuilder install. See the harvard-drs
#						SVN in TBRCTools/scripts or visit:
#
#							http://hul.harvard.edu/ois/systems/drs/drs2-software.html
#
# This script copies and renames the outlines in each folder of each Work listed in the
# worksList. The images are copied into the project/template/textOutline directory. (see the project.conf)
#
# Then the batchbuildercli.sh is called to create the batch directory structure in the 
# project directory. After this, the batchbuildercli.sh is called again to create the control
# files: batch.xml and descriptor.xml which are used to control the DRS import.
#
# The approach is to copy the projectMaster to make a new project that will contain a batch for
# for each Work to be deposited.
#

#
# Calculate the full path to an outline.The algorithm is
# outlineSrcRoot/substring(md5( $RID))
#
# Arguments: 	outlineSrcRoot:	parent of the buckets which contain the TTL files
# 				RID:  		work Id
function calcArchivePath() {
	_archive=$1
	_workId=$2
	_bucket=$(echo -n $_workId | md5 )
	_bucket=${_bucket:0:2}
	echo ${_archive}/${_bucket}/${_workId}.ttl
} 

# Variables and structure from ftpScript.sh
ME=$(basename $0)
ME_DIR=$(dirname $0)


#section error logging. Requires trailing
# Output is var ERR_LOG, ERROR_TXT, INFO_TXT variables
. ${ME_DIR}/setupErrorLog.sh "${ME}"
#endsection Set up logging

if [ "$#" -ne 5 ]; then
	echo "${ME}: Needs 5 parameters"
	echo "Usage: make-drs-outline worksList projectMasterDir targetProjectDir outlineParentDir bbDir"
	exit 1
fi

# jsk: need full path to script for components
 MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

worksList=${1?${ME}:${ERROR_TXT}:worksList is required}
echo Works List File: $worksList
if [ ! -f $worksList ]; then
	echo "${ME}: worksList \'${1}\' does not exist or is not a directory"
	exit 2
fi

projectMaster=${2?${ME}:${ERROR_TXT}:projectMaster is required}
echo BB Project Directory: $projectMaster
if [ ! -d $projectMaster ]; then
	echo "${ME}: projectMaster \'${2}\' does not exist or is not a directory"
	exit 2
fi
masterProjConf=$projectMaster/project.conf

#
# TargetProjectDir
# jsk: Target project might be absolute
targetProjectDir=${3?${ME}:${ERROR_TXT}:targetProjectDir is required}

outlineSrcRoot=${4?${ME}:${ERROR_TXT}:outlineSrcRoot is required}
echo Archive Directory: $outlineSrcRoot | tee -a $LOG_FILE
if [ ! -d $outlineSrcRoot ]; then
	echo "${ME}: outlineSrcRoot \'${4}\' does not exist or is not a directory"
	exit 2
fi

bbDir=$5
bb=batchbuildercli.sh

echo BB: $bbDir $bb | tee -a $LOG_FILE
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
templateDir=$targetProjectDir/template/textOutline

logPath=$targetProjectDir/bb-console.txt

echo Target Project Directory: $targetProjectDir

if [ -e $targetProjectDir ]; then
	echo "$(logDate):${ME}:${FATAL_TXT}:targetProjectDir ${targetProjectDir} already exists. Remove it or use a different name" | tee -a $logPath
	exit 2
fi

# jimk: 24.IV.2018: dont care if directory exists
mkdir -p "$targetProjectDir"

echo targetProjectDir: $targetProjectDir  | tee -a $logPath

# create a BB project to hold the batches that will be created
# We do this once to initiate the template dirs. Note that
# the original project conf is repeatedly overwritten

cp $masterProjConf $targetProjectDir  2>&1 | tee -a $logPath

# Fill in the template

echo $bb -a templatedirs -p $targetProjectDir  | tee -a $logPath 
$bb -a templatedirs -p $targetProjectDir 2>&1 | tee -a $logPath

targetConf="$targetProjectDir/project.conf"

echo Template Image Directory: $templateDir

echo Works List File: $worksList | tee -a  $logPath
echo BB Project Directory: $projectMaster | tee -a  $logPath
echo Target Project Name: $targetProjectDir | tee -a  $logPath
echo Outline parent Directory: $outlineSrcRoot | tee -a $logPath
echo Template Image Directory: $templateDir | tee -a  $logPath
echo Target Conf: $targetConf

while IFS=',' read -ra LINE; do
	RID=${LINE[0]}
	HID=${LINE[1]}

	echo TBRC $RID at HOLLIS $HID | tee -a  $logPath

	batchName=outline"$RID"
	echo Batch Name: $batchName | tee -a  $logPath

	java -jar "${MEPATH}/saxonhe-9.4.0.7.jar" $masterProjConf ${MEPATH}/make-proj-conf.xsl hId=$HID > $targetConf
	rc=$?

	[ $rc == 0 ] || { echo ${ME}:${FATAL_TXT}:Could not transform config file  $masterProjConf  rc= $rc ; break ; }

	outlineSourcePath=$(calcArchivePath $outlineSrcRoot $RID)

	# Make the OSN
	outlineBaseName=$(basename $outlineSourcePath)
	ext="${outlineBaseName##*.}"
	fnm="${outlineBaseName%.$ext}"

    destNm=${fnm}--outline.${ext}

	java -jar ${MEPATH}/drsttl-0.1.0.jar -i $outlineSourcePath > $templateDir/$destNm
	rc=$?
	[ $rc == 0 ] || { echo ${ME}:${FATAL_TXT}:Could not transform TTL file $outlineSourcePath rc= $rc ; break; }

    echo $bb -a buildtemplate -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath
    $bb -a buildtemplate -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath

    echo $bb -a build -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath

    # { time $bb -a build -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath ; } 2>> $TIMING_LOG_FILE
    $bb -a build -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath

    [ -f $targetProjectDir/$batchName/batch.xml ] || {
        echo ${ME}:ERROR:BB failed for $batchName  2>&1 | tee -a $logPath ;

        # We could decide to continue
        # exit 1;
    }
done < $worksList

#! /bin/bash

# script to collect imagegroups into a batch for processing via BatchBuilder and
# upload to Harvard Digital Repository Service
#
# this script is called as follows:
#
#     make-drs-batch.sh worksList projectMaster targetProject archiveDir bbDir
#
# the arguments are:
#
#		worksList		is a text file each line of which is a pair of TBRC RID,Hollis ID
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
declare -a BANNED_EXT=('db' 'DS_Store' )


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
mkdir -p "$targetProjectDir"

echo targetProjectDir: $targetProjectDir  >> $logPath 2>&1
# 
# Start timing log

# create a BB project to hold the batches that will be created
#

cp  -v $masterProjConf $targetProjectDir 2>&1 |tee -a  $logPath


while IFS=',' read -ra LINE; do
	RID=${LINE[0]}
	HID=${LINE[1]}
	echo TBRC $RID at HOLLIS $HID

	batchNameBase="batch$RID"
	
	start=0
	for part in $(seq 1 ${numBatches%.*}) ; do
		# create a batch for the current slice of the array of volumes
	

		batchName="$batchNameBase-$part"
		mkdir -p $targetProjectDir/$batchName
		touch $targetProjectDir/$batchName/batch.xml 
		
	done
	sleep 4s
done < $worksList
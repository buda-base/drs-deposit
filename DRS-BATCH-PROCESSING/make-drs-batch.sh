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
# The following needs to be reworked so that copying the project is done inside the loop
# and the update to the project.conf is performed followed by running the bb inside the
# loop - once for each line of the $worksList

if [ "$#" -ne 5 ]; then
	echo "Needs 5 parameters"
	echo "Usage: make-drs-batch worksList projectMaster targetProject archiveDir bbDir"
	exit 1
fi

workingDir=`pwd`

worksList=$1
echo Works List File: $worksList
if [ ! -f $worksList ]; then
	echo "worksList file does not exist"
	exit 2
fi

projectMaster=$2
echo BB Project Directory: $projectMaster
if [ ! -d $projectMaster ]; then
	echo "projectMaster does not exist or is not a directory"
	exit 2
fi
projConf=$projectMaster/project.conf

targetProject=$3
echo Target Project Name: $targetProject
if [ -e $targetProject ]; then
	echo "targetProject already exists. Remove it or use a different name"
	exit 2
fi
targetConf="$targetProject/project.conf"

archiveDir=$4
echo Archive Directory: $archiveDir
if [ ! -d $archiveDir ]; then
	echo "archiveDir does not exist or is not a directory"
	exit 2
fi

bbDir=$5
bb=./batchbuildercli.sh
echo BB: $bbDir $bb
if [ ! -d $bbDir ]; then
	echo "BatchBuilder directory does not exist"
	exit 2
fi
if [ ! -f $bbDir/$bb ]; then
	echo "batchbuildercli.sh does not exist in $bbDir"
	exit 2
fi

volsPerBatch=30
echo Volumes per Batch: $volsPerBatch

# create a BB project to hold the batches that will be created
cp -R $projectMaster $targetProject


projectDir=$workingDir/$targetProject
templateDir=$targetProject/template/image
echo Template Image Directory: $templateDir

echo Works List File: $worksList >> $projectDir/bb-console.txt 2>&1
echo BB Project Directory: $projectMaster >> $projectDir/bb-console.txt 2>&1
echo Target Project Name: $targetProject >> $projectDir/bb-console.txt 2>&1
echo Archive Directory: $archiveDir >> $projectDir/bb-console.txt 2>&1
echo Template Image Directory: $templateDir >> $projectDir/bb-console.txt 2>&1
echo Volumes per Batch: $volsPerBatch >> $projectDir/bb-console.txt 2>&1


while IFS=',' read -ra LINE; do
	RID=${LINE[0]}
	HID=${LINE[1]}
	echo TBRC $RID at HOLLIS $HID
	echo TBRC $RID at HOLLIS $HID >> $projectDir/bb-console.txt 2>&1
	cd $workingDir
	# make a custom project.conf for the current work
	java -jar saxonhe-9.4.0.7.jar $projConf make-proj-conf.xsl hId=$HID > $targetConf
	imagesDir=$archiveDir/$RID/images
	batchNameBase="batch$RID"
	echo Batch Name base: $batchName
	echo Images Directory: $imagesDir
	echo Images Directory: $imagesDir >> $projectDir/bb-console.txt 2>&1
	
	declare -a volNms=($imagesDir/*)
	numVols=${#volNms[@]}
	numBatches=$(((numVols + volsPerBatch - 1) / volsPerBatch))
	
	start=0
	for part in $(seq 1 ${numBatches%.*}) ; do
		# create a batch for the current slice of the array of volumes
		for v in ${volNms[@]:start:volsPerBatch} ; do
			# for each volume in the slice cp and rename the images
			echo ImageGroup Directory: $v
			echo ImageGroup Directory: $v >> $projectDir/bb-console.txt 2>&1
			pdsName=$(basename $v)
			seq=1
			
			for f in $v/* ; do
			# do the cp and rename of each image
				fullNm=$(basename $f)
				ext="${fullNm##*.}"
				fnm="${fullNm%.$ext}"
				suffix=$(printf %04d $seq)
				destNm="$pdsName--${fnm}__${suffix}.$ext"
				cp $f $templateDir/$destNm
				seq=$[seq + 1]
			done
		done

		batchName="$batchNameBase-$part"
		cd $bbDir
		echo $bb -a buildtemplate -p $projectDir -b $batchName
		echo $bb -a buildtemplate -p $projectDir -b $batchName >> $projectDir/bb-console.txt 2>&1
		$bb -a buildtemplate -p $projectDir -b $batchName >> $projectDir/bb-console.txt 2>&1
	
		echo $bb -a build -p $projectDir -b $batchName
		echo $bb -a build -p $projectDir -b $batchName >> $projectDir/bb-console.txt 2>&1
		$bb -a build -p $projectDir -b $batchName >> $projectDir/bb-console.txt 2>&1
		
		if [ -f $projectDir/$batchName/batch.xml ]; then
			mv $projectDir/$batchName/batch.xml $projectDir/$batchName/batch.xml.wait
		else
			echo BB failed for $batchName
			echo BB failed for $batchName >> $projectDir/bb-console.txt 2>&1
		fi
		
		cd $workingDir
		start=$[start + volsPerBatch]
	done
done < $worksList

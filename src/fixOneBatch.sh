#! /bin/bash -vx

# script to collect imagegroups into a batch for processing via BatchBuilder and
# upload to Harvard Digital Repository Service
#
# this script is called as follows:
#
#     fix-one-batch.sh workVolumes  targetProject  bbDir
#
# the arguments are:
#		targetProject	is the name of the project that will contain the generated batches
#
#		bbDir			this is the path to the directory containing batchbuildercli.sh and
#						supporting files - i.e., the BatchBuilder install. See the harvard-drs
#						SVN in TBRCTools/scripts or visit:
#
#							http://hul.harvard.edu/ois/systems/drs/drs2-software.html
#
# Processing:
# After some setup of source and targets, this script's main processing loop:
#   - Reads each line of the input file
#   - It's either a header line, which creates a new batch project, or it's
#       a data line, which gives the volume which will be added as an object in the
#       current batch project.
#
# Adding to an existing batch:
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

function doBatch {
    srcDir=$1
    batchName=$(basename ${srcDir})
    [ -z "${batchName}" ] && return

    $bb -a build -p ${srcDir} -b $batchName 2>&1  | tee -a  $logPath 

    if [ ! -f ${srcDir}/${batchName}/batch.xml ] ; then
	echo ${ME}:ERROR:BB failed for ${batchName} | tee -a ${logPath}
	update_build_status $DbConnectionString "${srcDir}" "FAIL"
    else
		    # set up mets
	td=$(mktemp -d)
	tojsondimensions.py -i ${srcDir} -o ${td} 2>&1 | tee -a ${logPath}
	rm -rf ${td}  2>&1 | tee -a ${logPath}
		    #
		    # jimk 2018-VI-17
	mv  ${targetProjectRoot}/${batchName} $OUTPUTHOME  2>&1 | tee -a ${logPath}
	update_build_status $DbConnectionString "${OUTPUTHOME}/${batchName}" "success"
    fi

}

#------------------          CONSTANTS   ------------------

# Set empty when running
DEBUGECHO=HOWDY echo

OUTPUTHOME=/Volumes/DRS_Staging/DRS/prod/batchBuilds

#
# jimk drs-deposit-108 2022-12-20 ; get literal files out of git
if [[ -z $DB_CONN ]]
then
    printf "FATAL: Cannot connect to database"
    exit 42
fi

DbConnectionString='-d ' ${BB_LEVEL}:{$DB_CONN}

# Who's running?
ME=$(basename ${0})

if [ "$#" -ne 2 ]; then
    echo "${ME}: Needs 2 parameters"
    echo "Usage: ${ME}  targetProjectRoot bbDir"
    exit 1
fi

# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

bbDir=$2
bb=batchbuildercli.sh

echo BB: ${bbDir} ${bb}
if [ ! -d ${bbDir} ]; then
    echo "${ME}: BatchBuilder directory  \'${5}\' does not exist or is not a directory"
    exit 2
fi
if [ ! -f ${bbDir}/${bb} ]; then
    echo "${ME}: batchbuildercli.sh does not exist in $bbDir"
    exit 2
fi
bb=${bbDir}/${bb}
# jimk 24.1.18: copy  batchbuilder logs, including failed files
bbLogDir=${bbDir}/logs


# jsk: Target project might be absolute
targetProjectRoot=$1

# BIG difference - keep the bb-console local
logPath=./bb-console.txt

echo Target Project Directory: ${targetProjectRoot}

if [ ! -e ${targetProjectRoot} ]; then
    echo "${ME}: targetProjectRoot ${targetProjectRoot} must exist but does not."

    exit 2
fi

batchName=$(basename ${targetProjectRoot})
doBatch $targetProjectRoot ${batchName}
# clean up log
mv $logPath ${batchName}.log 

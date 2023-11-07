#!/usr/bin/env bash

# script to collect transformed printMasters into a batch for processing via BatchBuilder and
# upload to Harvard Digital Repository Service
#
# this script is called as follows:
#
#     make-drs-printMaster.sh worksList projectMaster targetProject archiveDir bbDir
#
# the arguments are:
#
#		workList		is the path to a text file each whose format is given in
#                       drs-deposit/src/BatchBuilding.md
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
#		printMasterSrcRoot	is the path to the printMaster archive from which this script retrieves
#						the printMasters. This archive is only folders, named after first two characters
#						of the MD5 has of the works they contain
#
#		bbDir			this is the path to the directory containing batchbuildercli.sh and
#						supporting files - i.e., the BatchBuilder install. See the harvard-drs
#						SVN in TBRCTools/scripts or visit:
#
#							http://hul.harvard.edu/ois/systems/drs/drs2-software.html
#
# This script copies and renames the printMasters in each folder of each Work listed in the
# worksList. The images are copied into the project/template/document_printmaster directory. (see the project.conf)
#
# Then the batchbuildercli.sh is called to create the batch directory structure in the 
# project directory. After this, the batchbuildercli.sh is called again to create the control
# files: batch.xml and descriptor.xml which are used to control the DRS import.
#
# The approach is to copy the projectMaster to make a new project that will contain a batch for
# for each Work to be deposited.
#



# Variables and structure from ftpScript.sh
ME=$(basename $0)

# jsk: need full path to script for components
MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

# This is the final output home, where successful batch builds go
OUTPUTHOME=/Volumes/DRS_Staging/DRS/${BB_LEVEL}/batchBuilds

#
# jimk drs-deposit-108 2022-12-20 ; get literal files out of git
if [[ -z $DB_CONN ]]
then
    printf "FATAL: Cannot connect to database"
    exit 42
fi

DbConnectionString='-d '${BB_LEVEL}:$DB_CONN

#--------------------------------------------------
#section error logging. Requires trailing
# Output is var ERR_LOG, ERROR_TXT, INFO_TXT variables
. ${MEPATH}/setupErrorLog.sh "${ME}"
#endsection Set up logging
#--------------------------------------------------

#--------------------------------------------------
#section Commmon utils
source ${MEPATH}/commonUtils.sh
#endsection Common utils
#--------------------------------------------------
# -------------   doBatch    ----------------------

function doBatch {
    [ -z "${batchName}" ] && return

    echo ${bb} -a buildtemplate -p ${targetProjectDir} -b ${batchName} | tee -a ${logPath}
    ${bb} -a buildtemplate -p ${targetProjectDir} -b ${batchName} >> ${logPath} 2>&1

        # build results into batch
    echo $bb -a build -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath

    $bb -a build -p $targetProjectDir -b $batchName  2>&1 | tee -a $logPath

	if [ ! -f ${targetProjectDir}/${batchName}/batch.xml ] ; then
	    echo ${ME}:ERROR:BB failed for ${batchName} | tee -a ${logPath}
	    updateBuildStatus $DbConnectionString "${targetProjectDir}/${batchName}" "FAIL"
	else
	    mv -v --backup=numbered  ${targetProjectDir}/${batchName} $OUTPUTHOME  2>&1 | tee -a ${logPath}
	    updateBuildStatus $DbConnectionString "${OUTPUTHOME}/${batchName}" "success"
	fi

    cleanUpLogs ${batchName}
}
#--------------------------------------------------
#section Arg validation
if [ "$#" -ne 5 ]; then
	echo "${ME}: Needs 5 parameters"
	echo "Usage: make-drs-printMaster worksList projectMasterDir targetProjectDir printMasterParentDir bbDir"
	exit 1
fi

worksList=${1?${ME}:${ERROR_TXT}:worksList is required}
echo Works List File: ${worksList}
if [ ! -f ${worksList} ]; then
	echo "${ME}: worksList \'${1}\' does not exist or is not a directory"
	exit 2
fi

projectMaster=${2?${ME}:${ERROR_TXT}:projectMaster is required}
echo BB Project Directory: ${projectMaster}
if [ ! -d ${projectMaster} ]; then
	echo "${ME}: projectMaster \'${2}\' does not exist or is not a directory"
	exit 2
fi
masterProjConf=${projectMaster}/project.conf

#
# TargetProjectsRoot
# jsk: Target project might be absolute

targetProjectDir=${3?${ME}:${ERROR_TXT}:targetProjectDir is required}

logPath=${targetProjectDir}/bb-console.txt


printMasterSrcRoot=${4?${ME}:${ERROR_TXT}:printMasterSrcRoot is required}
echo Archive Directory: ${printMasterSrcRoot} | tee -a $LOG_FILE
if [ ! -d $printMasterSrcRoot ]; then
	echo "${ME}: printMasterSrcRoot \'${4}\' does not exist or is not a directory"
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

# overload $bb
bb=${bbDir}/$bb
# jimk 24.1.18: copy  batchbuilder logs, including failed files
bbLogDir=${bbDir}/logs


# template dir path suffix (template/image) is defined in the project conf. If changed there,
# must be changed here.
templateDir=${targetProjectDir}/template/document_printMasters

logPath=${targetProjectDir}/bb-console.txt

echo Target Project Directory: ${targetProjectDir}

if [ -e $targetProjectDir ]; then
	echo "$(logDate):${ME}:${FATAL_TXT}:targetProjectDir ${targetProjectDir} already exists. Remove it or use a different name" | tee -a ${logPath}
	exit 2
fi

# jimk: 24.IV.2018: don't care if directory exists
mkdir -p "$targetProjectDir"

echo targetProjectDir: ${targetProjectDir}  | tee -a ${logPath}

# create a BB project to hold the batches that will be created
# We do this once to initiate the template dirs. Note that
# the original project conf is repeatedly overwritten

cp ${masterProjConf} ${targetProjectDir}  2>&1 | tee -a ${logPath}

# Fill in the template

echo ${bb} -a templatedirs -p ${targetProjectDir}  | tee -a ${logPath}
${bb} -a templatedirs -p ${targetProjectDir} 2>&1 | tee -a ${logPath}

targetConf="$targetProjectDir/project.conf"

echo Template Image Directory: ${templateDir}

echo Works List File: ${worksList} | tee -a  ${logPath}
echo BB Project Directory: $projectMaster | tee -a  $logPath
echo Target Project Name: $targetProjectDir | tee -a  $logPath
echo Print Master parent Directory: $printMasterSrcRoot | tee -a $logPath
echo Template Image Directory: $templateDir | tee -a  $logPath
echo Target Conf: $targetConf

# This loop is a modification of the loop in make-drs-batch.sh
# instead of image groups, it creates a DRS deposit object for each print master under each work.
# (Analagous to create a deposit object for each volume, except the deposit object only contains one
# file.


#Declare here, loop fills in
declare batchName=
declare firstLine=


while IFS=',' read -ra LINE; do
 # skip the first line. It's just a header line
    [ -z ${firstLine} ] &&  {
            firstLine=1;
            continue;
    }
	RID=${LINE[0]}
	HID=${LINE[1]}
	VID=${LINE[2]}

	if $(isNewHeaderLine LINE[@]) ; then
        doBatch ;
     else
        echo TBRC $RID at HOLLIS $HID Volume $VID | tee -a  $logPath

        # This *should* be the same for every line in a group, otherwise it becomes the last one.
        batchName=printMaster${RID}
        echo Batch Name: $batchName | tee -a  $logPath

        # Inject the HOLLIS id into the printMaster's project.conf
        java -jar "${MEPATH}/saxonhe-9.4.0.7.jar" $masterProjConf ${MEPATH}/make-proj-conf.xsl hId=$HID > $targetConf
        rc=$?

        [ $rc == 0 ] || { echo ${ME}:${FATAL_TXT}:Could not transform config file  $masterProjConf  rc= $rc ; break ; }

        # use the input line to locate each file.
        # the rename will have a different OSN for each file. See
        # https://wiki.harvard.edu/confluence/display/LibraryStaffDoc/3.+Naming+and+Metadata+Rules#id-3.NamingandMetadataRules-Objectownersuppliednames
        # This has the effect of creating one object of DOCUMENT type for each file.
        # The object's OSN also corresponds to the label of the Volume table's (See drs db)entry for the print master.
        # See also DBApps/DRSUpdate.py: 24
        # "Muy importante!  OSN corresponds to Volume, and is used as the FK from DRS to Volume in the DB Trigger



        pmFileBase=${printMasterSrcRoot}/$RID/prints/${VID}
        for f in ${pmFileBase}* ; do

            # This transform makes each file its own object. The string
            # before the -- separator becomes the OSN for the object. The file retains the
            # name
            destName="${VID}--$(basename ${f})"

            cp ${f} ${templateDir}/${destNm} 2>&1 | tee -a ${logPath}

            declare -i rc=${PIPESTATUS[0]}
            if ((${rc} != 0 )); then
                echo   cp ${pmFile} ${templateDir}/${destNm}	failed rc: ${rc} | tee -a ${logPath}
                exit ${rc}       # Just fail here
            fi
        done
    fi


done < $worksList
doBatch

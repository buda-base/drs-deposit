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
#		workList		is the path to a text file each whose format is given in
#                       drs-deposit/DRS-BATCH-PROCESSING/BatchBuilding.md
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



#------------------          CONSTANTS   ------------------
# Who's running?
ME=`basename ${0}`

# First, do no harm

[ -z "$BB_LEVEL" ] &&  { echo ${ME}':error:BB level not set' ; Usage ; exit 1; }


TIMING_LOG_FILE=timeBuildBatch.log
# bash builtin time format
TIMEFORMAT=$'%R\t%U\t%S\t%P'
export TIMEFORMAT

OUTPUTHOME=/Volumes/DRS_Staging/DRS/$BB_LEVEL/batchBuilds

DbConnectionString='-d '${BB_LEVEL}':~/.drsBatch.config'

# Harvard Name resolver URIs. See generateHulNrsUrn()
# HACK: must contain trailing /
prodNRS=https://nrs.lib.harvard.edu/
qaNRS=https://nrs-qa.lib.harvard.edu/



if [ "$#" -ne 5 ]; then
	echo "${ME}: Needs 5 parameters"
	echo "Usage: make-drs-batch worksList projectMaster targetProjectDir archiveDir bbDir"
	exit 1
fi

# jsk: need full path to script for components
 MEPATH="$( cd "$(dirname "$0")" ; pwd -P )"

# jsk 12.21.17 ##https://github.com/BuddhistDigitalResourceCenter/drs-deposit/issues/14
# Filter out banned extensions
declare -a BANNED_EXT=('tmp' 'png' 'pdf' 'db' 'DS_Store' )

#  --- common utilities
source ${MEPATH}/commonUtils.sh


function toLower() {
	echo $1 | tr '[:upper:]' '[:lower:]'
}
#
# return true (0) if an extension is banned
function isBannedExt() {
	testExt=$(toLower "$1")
	for anExt in ${BANNED_EXT[@]} ; do
		[ "$testExt" == "$(toLower ${anExt})"  ] && return 0;
    done
	return 1 
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
	array=${@:1:${wordsInArgs}}

	for s in ${array} ; do
		testString=$(printf " %s %s" ${testString} ${s})
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
	[ ${maxLength} -le 0 ] && return

	# invert maxlength, to get end of string
	result=""
	maxLength=-${maxLength}

	while [ -z "$result" -a ${maxLength} -lt 0 ] ; do
		testNum=${testString: maxLength}
		#
		# See above
		[ -z "${testNum//[0-9]}" ] && [ -n "$testNum" ] || { 
			d=$((maxLength++))
			continue
		}
	echo ${testNum}
	return
done
return
}


function doBatch {
        [ -z "${batchName}" ] && return

        echo ${bb} -a buildtemplate -p ${targetProjectDir} -b ${batchName} | tee -a ${logPath}
        ${bb} -a buildtemplate -p ${targetProjectDir} -b ${batchName} >> ${logPath} 2>&1

        # build results into batch


        # { time $bb -a build -p $targetProjectDir -b $batchName >> $logPath 2>&1 ; } 2>> $TIMING_LOG_FILE
        #  DO REAL WORK
        # Note I'm deliberately redirecting all output to log file - this is a noisy process.
		echo ${bb} -a build -p ${targetProjectDir} -b ${batchName}   | tee -a ${logPath}
        ${bb} -a build -p ${targetProjectDir} -b ${batchName} >> ${logPath} 2>&1

		if [ ! -f ${targetProjectDir}/${batchName}/batch.xml ] ; then
			echo ${ME}:ERROR:BB failed for ${batchName} | tee -a ${logPath}
			updateBuildStatus ${DbConnectionString} "${targetProjectDir}/${batchName}" "FAIL" 2>&1 | tee -a ${logPath}
		else
		    # set up mets
		    td=$(mktemp -d)
		    tojsondimensions.py -i ${targetProjectDir}/${batchName} -o ${td} 2>&1 | tee -a ${logPath}
		    rm -rf ${td}  2>&1 | tee -a ${logPath}
		    #
		    # jimk 2018-VI-17
		    # WARN: buildSendList now has to filter out backfile directories ( *~) from its
		    # list.
		    mv -v --backup=numbered ${targetProjectDir}/${batchName} ${OUTPUTHOME}  2>&1 | tee -a ${logPath}
		    updateBuildStatus ${DbConnectionString} "${OUTPUTHOME}/${batchName}" "success"  2>&1 | tee -a ${logPath}
		fi
        # jimk 2018-V-18: this used to be above the last fail.
       cleanUpLogs ${batchName}

}

#
# Generate an Urn that can turn a DRS file Urn into a resolvable URI
#
# arguments:
#  $1: any string.
#  if null, just return nothing.
# otherwise, prepend with the resolver server, set in SetBBLevel.sh
function generateHulNrsUrn() {
    [ -z "$1" ] && return ;
    echo ${HUL_NRS_RESOLVER_URL%%/}/$1
}




worksList=$1
echo Works List File: ${worksList}
if [ ! -f ${worksList} ]; then
	echo "${ME}: worksList \'${1}\' does not exist or is not a directory"
	exit 2
fi

projectMaster=$2
echo BB Project Directory: ${projectMaster}
if [ ! -d ${projectMaster} ]; then
	echo "${ME}: projectMaster \'${2}\' does not exist or is not a directory"
	exit 2
fi
masterProjConf=${projectMaster}/project.conf

archiveDir=$4
echo Archive Directory: ${archiveDir}
if [ ! -d ${archiveDir} ]; then
	echo "${ME}: archiveDir \'${4}\' does not exist or is not a directory"
	exit 2
fi

bbDir=$5
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
targetProjectDir=$3

logPath=${targetProjectDir}/bb-console.txt

echo Target Project Directory: ${targetProjectDir}

if [ -e ${targetProjectDir} ]; then
	echo "${ME}: targetProjectDir ${targetProjectDir} already exists. Remove it or use a different name"
	exit 2
fi
mkdir "$targetProjectDir"

echo targetProjectDir: ${targetProjectDir}  >> ${logPath} 2>&1
#
# Start timing log
# echo Create target dir

cp ${masterProjConf} ${targetProjectDir}  2>&1 | tee -a ${logPath}

# Fill in the template. Do this once per root. Not needed
# once per batch

echo ${bb} -a templatedirs -p ${targetProjectDir} | tee -a ${logPath}
${bb} -a templatedirs -p ${targetProjectDir} 2>&1 | tee -a ${logPath}

targetConf="$targetProjectDir/project.conf"


# template dir path suffix (template/image) is defined in the project conf. If changed there,
# must be changed here.
templateDir=${targetProjectDir}/template/image


# 30 is about 18 - 20000 files, which is too
# many for poor old DRS.
declare -i volsPerBatch=20
echo Volumes per Batch: ${volsPerBatch}

echo Template Image Directory: ${templateDir}

echo Works List File: ${worksList} >> ${logPath} 2>&1
echo BB Project Directory: ${projectMaster} >> ${logPath} 2>&1
echo Target Project Root: ${targetProjectDir} >> ${logPath} 2>&1
echo Archive Directory: ${archiveDir} >> ${logPath} 2>&1
echo Template Image Directory: ${templateDir} >> ${logPath} 2>&1
echo Volumes per Batch: ${volsPerBatch} >> ${logPath} 2>&1

#Declare here, loop fills in
batchName=
declare -i thisBatchVolCount=0
declare firstLine=
declare -i batchesThisWork=1

# delete the first line of workfile, using sed, into a $(mktemp)
# cat rest | parallel
# cat ${worksListFile} | parallel , using , as a parameter separator
# watch out for times. This routine makes directories based on time.
# function_called  {1} {2} {3} {4} {5}
while IFS=, read -ra LINE ; do
    # skip the first line
    [ -z ${firstLine} ] &&  {
            firstLine=1;
            continue;
    }
    # put the rest of this loop into function_called
    RID=${LINE[0]}
    HID=${LINE[1]}
    VID=${LINE[2]}
    OutlineUrn=$(generateHulNrsUrn ${LINE[3]})
    PrintMasterUrn=$(generateHulNrsUrn ${LINE[4]})

    # Sanity check - have we built this volume somewhere else?
    thisVolBuildPath=$(find ${OUTPUTHOME} -maxdepth 2 -mindepth 2 -type d  -name ${VID} )
    [ ! -z ${thisVolBuildPath} ] && {
        echo "Skipping: $thisVolBuildPath already built" | tee -a ${logPath}
    continue
    }

    if   (($thisBatchVolCount == $volsPerBatch )) ||  $(isNewHeaderLine LINE[@]) ; then
      doBatch
      if (($thisBatchVolCount == $volsPerBatch ))  ; then
        batchesThisWork+=1
      else
        batchesThisWork=1
      fi
       thisBatchVolCount=0
    else

        # Are we starting a new batch?
        if (($thisBatchVolCount == 0)) ; then
            echo TBRC ${RID} at HOLLIS ${HID} | tee -a  ${logPath}
            java -jar "${MEPATH}/saxonhe-9.4.0.7.jar" ${masterProjConf} ${MEPATH}/make-proj-conf.xsl hId=${HID}   outlineUrn=${OutlineUrn} printMasterUrn=${PrintMasterUrn} > ${targetConf}

            # jimk 2018-VI-18: Append new with n.
            # jimk 2018-VII-18: add short hashtag
	    mdDate=$(date +%H%M%S | md5)
	    mdDate=${mdDate:0:2}
            batchName=$(printf "%s-%d-%s" "batch$RID" ${batchesThisWork} $mdDate)
            echo Batch Name: ${batchName} | tee -a  ${logPath}
        fi

        imagesDir=${archiveDir}/${RID}/images/${VID}
        echo ImageGroup Directory: ${imagesDir} | tee -a ${logPath}
        pdsName=${VID}

        for f in ${imagesDir}/* ; do
        # cp and rename each image
            fullNm=$(basename ${f})
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
                    echo ${ME}:WARNING: Skipping invalid sequence in work ${RID} volume ${pdsName} ${fnm} | tee -a ${logPath}
                continue
            }

            # This transform makes the file name comply with PDS sequencing
            destNm="$pdsName--${fnm}__${suffix}.$ext"
            cp ${f} ${templateDir}/${destNm} 2>&1 | tee -a ${logPath}

            declare -i rc=$?
            if ((${rc} != 0 )); then
                echo cp ${f} ${templateDir}/${destNm}	failed rc: ${rc} | tee -a ${logPath}
                exit ${rc}       # Just fail here
            fi
        done
        thisBatchVolCount+=1

    fi
done < ${worksList}
doBatch

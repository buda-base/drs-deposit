#!/usr/bin/env bash -vx
# Arrange mock
MEPATH=$dd/RelatedURNInject/bin
export outPath=$dd/RelatedURNInject/output/
export HID="HOLLISIDPARAM"
export targetConf="Injected.xml"
export masterProjConf="${MEPATH}/project.conf"

# This is a scrape of SetBBLevel.sh for qa
#################################################
export PROD_BB_LEVEL=prod
export QA_BB_LEVEL=qa


export BB_LEVEL=$QA_BB_LEVEL

# Set up the nrs resolver for injecting into project.conf
# See DRS-BATCH-PROCESSING/make-drs-batch.conf

prodNRS=https://nrs.lib.harvard.edu/
qaNRS=https://nrs-qa.lib.harvard.edu/


levels=${BB_LEVEL}NRS
export HUL_NRS_RESOLVER_URL=${!levels}


##################################################

export iCt=0

while IFS=: read -ra lineArgs ; do
    printMasterURI=
    outlineURI=
    [ ! -z "${lineArgs[0]}" ] && { outlineURI=${HUL_NRS_RESOLVER_URL}${lineArgs[0]} ; }
    [ ! -z "${lineArgs[1]}" ] && { printMasterURI=${HUL_NRS_RESOLVER_URL}${lineArgs[1]} ; }

    ((iCt++))
    echo   ${outPath}${iCt}${targetConf}
    java -jar "${MEPATH}/saxonhe-9.4.0.7.jar" ${masterProjConf} ${MEPATH}/make-proj-conf.xsl outlineURI=${outlineURI}  printMasterURI=${printMasterURI} hId=${HID}  > ${outPath}${iCt}${targetConf}
done << YOW
:pmOnly
outlineOnly
outline:pm

YOW



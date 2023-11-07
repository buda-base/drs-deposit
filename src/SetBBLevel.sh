#@IgnoreInspection BashAddShebang
#   !/usr/bin/env bash
# Bash source file to set Batchbuilder level
# You have to inline this, calling won't work.
#
# Usage . <wherever>/SetBBLevel.sh [qa|prod]
#
# These are the only two values.
# they must be a suffix of one of the file
# in $BB_HOME/conf/bb.properties
# Case sensitive
#
# make-drs-batch.sh stops unless this value is set
export PROD_BB_LEVEL=prod
export QA_BB_LEVEL=qa

# jimk - apparently you can parse args to source
export BB_LEVEL=${1-$PROD_BB_LEVEL}

# Set up the nrs resolver for injecting into project.conf
# See src/make-drs-batch.conf

prodNRS=https://nrs.lib.harvard.edu/
qaNRS=https://nrs-qa.lib.harvard.edu/

export HUL_NRS_RESOLVER_URL=$(eval echo \$${BB_LEVEL}NRS)

# jimk drs-deposit-108
# User copies their configuration
echo export BB_SOURCE=<SET_YOUR_BATCH_BUILDER_PARENT_DIR_HERE> (e.g.) ~/DRS/BatchBuilder-2.2.19
echo export DbConnectionString=<SET YOUR DB CONNECTION HERE>

#
# 


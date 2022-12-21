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
# See DRS-BATCH-PROCESSING/make-drs-batch.conf

prodNRS=https://nrs.lib.harvard.edu/
qaNRS=https://nrs-qa.lib.harvard.edu/

export HUL_NRS_RESOLVER_URL=$(eval echo \$${BB_LEVEL}NRS)

export BB_SOURCE=~/DRS/BatchBuilder-2.2.19


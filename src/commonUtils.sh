#@IgnoreInspection BashAddShebang
# Common functions. this file is intended to be sourced, not executed
#
# Argument is the first token in a line. Tests for it to be a magic header
function isNewHeaderLine {
    seekTok=WorkName
    declare -a argA=$1
    [ "${argA[0]}" == "${seekTok}" ]
}

#
# copy logs for this batch builder run, and remove them
# requires definitions of:
#   targetProjectsRoot
#   bbLogDir
#   logPath

function cleanUpLogs() {
	  # jimk 21.I.18: copy batchbuilder log
	  batchLogDir=${targetProjectDir}/${1}"-"logs

        mkdir ${batchLogDir}
        # Keep al the logs for reference, but extract into a summary
        cp -R ${bbLogDir} ${batchLogDir}
        cp ${logPath} ${batchLogDir}
        rm -rf ${bbLogDir}
        rm -rf ${logPath}
        # Summarize and extract
        # jsk: issue #44: wasn't finding errors correctly.
        # find ... -name -o xyz -o -name abc doesn't look for abc when it finds abc
        find ${batchLogDir} -type f -not -name errorSummary.txt -exec grep -H -n -i 'err\|warn\|except' {} \; \
        >> ${batchLogDir}/errorSummary.txt
}

#
# Set up Batch builder home
#
function prepBBHome {
	# Copy BatchBuilder code to a location for this instance.
	# $MAKEDRS will copy the batchbuilder log to the
    # batch output directory
    [[ -d ~/tmp ]] && { mkdir ~/tmp ; }
	export BB_HOME=$(mktemp -d -p ~/tmp )
	cp -rp $BB_SOURCE/* $BB_HOME
	rm -f $BB_HOME/logs/*

	propFile="$BB_HOME/conf/bb.properties"
	[ -f $propFile ] && { rm -f $propFile ; }
	#
	# See <binFolder>/SetBBLevel.sh
	cp "${propFile}".${BB_LEVEL} "$propFile"
}

function cleanBBHome {
    rm -rf $BB_HOME
}



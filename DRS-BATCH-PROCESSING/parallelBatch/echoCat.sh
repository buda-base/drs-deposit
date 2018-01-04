#!/bin/bash -vx
# This fragment of code is an experiment to inject a return code into a process
# status file (runMultiple.sh creates underway and completed directories).
# Intended for use in recording the results of a completed process.
#
# Used at the end of makeOneDrs.sh
# 
# Test fragment which looks for a specfic process id in underway (80434) 
# From the file it finds, it:
# 1. Extracts the file name
# 2. Injects a current return code (the prior process return code)
# 3. Writes the results to the completed directory.
#
# Dependencies:
# 	${resultsDir} must exist.
#	'underway' directory must exist
	childRc="Howdy"
	resultsDir="tmp"
	#
	# move the process flag to done
	doneFile=$(find underway -type f -exec  grep -l  80434 {} /dev/null \;)
	doneFileName=$(basename $doneFile)
	doneFileName="${doneFileName%.*}"
	cat ${doneFile} | awk -v RC=${childRc} '{print $0":"RC }' > ${resultsDir}/$doneFileName

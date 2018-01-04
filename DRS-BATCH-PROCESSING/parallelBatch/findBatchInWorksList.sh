#!/bin/bash   
# Locates the works which are in progress in their workLists.
# Background:  make-drs-batch.sh takes as input a work list, which is a list of
# works and HOLLIS ids which it puts into a batch builder project.
# It runs through this list serially. 
# This script tracks the progress of the currently running batchbuilder processes,
# by using the 'java' command as a proxy for in progress batchbuilder commands.
#
# Dependencies: 
# 1. ps command: returns the command arguments last.
# 2. make-drs-batch.sh: this script expectes it to create folders named 'batchW****-****'
# 3. make-drs-batchsh:  use the -b batchW.... as the last argument to the batchbuildercli.sh command.
#
lstFile=$(mktemp)
#
# Get all the instances of java.
# get the last field
# Change batch@@@@@-***** to @@@@
# write all the results, one at a time, to lstfile.
ps -e | grep java | grep -v grep | awk '{print $NF}' | sed 's/^batch\([A-Z0-9]*\)\(-.*\)/\1/' > $lstFile
#
# Look for the work number in the work list. Print out the found file, and the line number
# In an ideal world, we'd count the number of lines in the file, and print a percentage complete,
# but the preparer should know how long a work list is.
grep -n -f  $lstFile bigRuns/*
#
# "I got no more use for this guy" -- Vinnie Gambino
rm $lstFile

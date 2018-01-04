#!/bin/bash
#
# Count the number of underway batches at the current time
#
# Dependencies:
# makeOneDrs.sh:  creates a directory for the underway statuses.
# Used here as the variable 'dir'

dir="timing/underway"

while true ; do
	files=(${dir}/*)
	# You always get 1 if the directory is empty
 	[ ${#files[@]} -eq 1 ] && break ;
  	printf "%s\t%d\n" $(date +%H:%M:%S) ${#files[@]}
  	sleep 120s
 done
 echo 'done'
#!/bin/bash

# Take 2: Use volumes - they are other directories where batchbuild is found
# Look in the directories containing batch.xml for directories
# Problematic that you
# for riji in $(find $PR -maxdepth 4 -name batch.xml);do find  $(dirname $riji) -maxdepth 1 -mindepth 1 -type d ; done | sort
#
#  Thanks SO for clever way to sort by last field
# Sort on the last field, reassemble the full paths.
# Then, scan each line, printing where the last field is different from the saved last field.
 for riji in $(find $PR -maxdepth 4 -name batch.xml);do   find  $(dirname $riji) -maxdepth 1 -mindepth 1 -type d ; done \
  | awk -F'/' '{print $NF,$0}'| sort | cut -f2 -d' ' \
  | awk -F'/' 'BEGIN {vol="CANTFIND"} { if ($NF != vol)  { print $0 ; vol = $NF } } '

# To get rid of the duplicates, use this awk instead
# $ rm rmDups
# 'BEGIN {vol="CANTFIND"; rmDups = "rmDups" } { if ($NF != vol)  { print $0 ; vol = $NF }else {print $0 >> rmDups  } } '
#
#

#!/bin/bash

# Take 2: Use volumes - they are other directories where batchbuild is found
# Look in the directories containing batch.xml for directories which are volumes
#  Thanks SO for clever way to sort by last field
# Sort on the last field, reassemble the full paths.
# Then, scan each line, printing where the last field is different from the saved last field.
#
# Explain:
# 1. find every batch under prod  ( for riji  in .... )
# 2. For each batch, find each volume. (find $(dirname $riji....) This gives all the deposited volumes under $PR
# 3. sort on the last field, by splitting it out and printing it before its path:   awk -F'/' '{print $NF,$0}'| sort | cut -f2 -d' '
# This has the effect of putting
# Now filter out the batches which have more than one volume in them.
 for riji in $(find $PR -maxdepth 4 -name batch.xml);do   find  $(dirname $riji) -maxdepth 1 -mindepth 1 -type d ; done \
  | awk -F'/' '{print $NF,$0}'| sort | cut -f2 -d' ' \
  | awk -F/ 'BEGIN {vol="CANTFIND"; rmDups = "rmDups" } { if ($NF != vol)  { print $0 ; vol = $NF }else {print $0 >> rmDups  } } '


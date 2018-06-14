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
## Not so fast: need to preserve the directories to keep one of the duplicates.
## the old algorithm was removing all instances of duplicates, we want to keep 1
#for riji in $(find $PR -maxdepth 4 -name batch.xml); do find  $(dirname $riji) -maxdepth 1 -mindepth 1 -type d ; done \
#| xargs -n 1 basename > allVolumes

sort allVolumes | uniq -c | grep -v '^ *1'

# Hah! k8 is the field separator
find $PR -name batch.xml -maxdepth 4 > allBuilds

# count duplicates
# k8 is the batch build. In a file of abs paths, /1/2/3/4/5, the folder '1' is actually key 2,
# (k1 is the empty field before the first /)
# so, in /Volumes/DRS_Staging/DRS/prod/20180326/worksList8.15.45/batchW1KG9278-1/batch.xml
# batchW.... is key 8

# cat allBuilds | sort -k8 -t/ | tr '/' ' ' | uniq -c -f 6 | grep -n '^ *2' | wc
#     494    4940   46067

# So, what I want is to take these, and remove the duplicates.
# Note the output, before the wc
# cat allBuilds | sort -k8 -t/ | tr '/' ' ' | uniq -c -f 6 | grep -n '^ *2' 
#
# 2:   2  Volumes DRS_Staging DRS prod 20180326 worksList1.10.46 batchW00CHZ0103335-1 batch.xml
# 3:   2  Volumes DRS_Staging DRS prod 20180330 worksList1.17.53 batchW00CHZ0103345-1 batch.xml
# 4:   2  Volumes DRS_Staging DRS prod 20180330 worksList1.18.09 batchW00EGS1016199-1 batch.xml
# Cut some fields and build a path:
# we want just worksList1.10.46/batchW00CHZ0103335-1
 cat allBuilds | sort -k8 -t/ | tr '/' ' ' | uniq -c -f 6 | grep '^ *2' | tr  ' ' '/' | cut -f 11,12 -d / > dupBatchPaths

if [ ! -s dupBatchPaths ] ; then 
    cp allBuilds BuildList.txt
else
    grep -v -f dupBatchPaths allBuilds > BuildList.txt
fi
# #
# And make this into a field selector for grep
# jimk@Khyung:getAllBuilds$ wc allBuilds
#     3817    3817  316339 allBuilds

    #
    # And it works:
#     jimk@Khyung:getAllBuilds$ fgrep -v -f dupBatchPaths allBuilds > tmptmp
# jimk@Khyung:getAllBuilds$ wc tmptmp
#     3323    3323  274733 tmptmp
# jimk@Khyung:getAllBuilds$ ls
# ab3           ab3r          allBuilds     allBuilds2    dupBatchPaths files         frelm         test          testScript.sh tmptmp
# jimk@Khyung:getAllBuilds$ wc ab3
#     3817   30536  316339 ab3
# jimk@Khyung:getAllBuilds$ rm ab3
# jimk@Khyung:getAllBuilds$ rm ab3r
# jimk@Khyung:getAllBuilds$ wc dupBatchPaths
#      494     494   17400 dupBatchPaths
# jimk@Khyung:getAllBuilds$ expr 494 + 3323
# 3817
# jimk@Khyung:getAllBuilds$


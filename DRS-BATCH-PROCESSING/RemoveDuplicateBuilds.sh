
#!/bin/bash


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
 grep -v -f dupBatchPaths allBuilds > BuildList.txt
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


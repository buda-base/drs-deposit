#!/usr/bin/awk -f
#
# Usage getVolumesForWork  <input file>
# Where Input file contains records, one per line
# in the form 'WorkName'
# and then reads the output of 'ls /Volumes/Archive/WorkName/images for
# its folders
# It then prints out
# the workname and the folder names.

# This gets the volumes in a work into a form
# where they can be added to the database 
#

function saveLs(dir,saveTo)
{
   cmd = "ls " "'"dir"'"
   while ( ( cmd | getline result ) > 0 ) {
        push(saveTo,  result)
    }
    close(cmd)
}


BEGIN{
    # make sure we have an array
    delete worksVolumes[0]
}
{

# For each
    delete worksVolumes

    work = $0
    workPath = "/Volumes/Archive/"  work "/images"
    # printf("length(pmpaths)=%d\twork Path = %s work=%s\n", length(pmpaths), workPath, work)
    saveLs(workPath,worksVolumes)
    nVolumes = length(worksVolumes)
    print $0,workPath, nVolumes
    for (i=0;i<nVolumes;i++){
       printf("\t%s\t%s\n", work,worksVolumes[i])
        }
}

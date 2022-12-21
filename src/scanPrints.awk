#!/usr/bin/awk -f
#
# Usage scanPrints <input file>
# Where Input file contains records, one per line
# in the form <ParentDir>*/WorkName/<oneMoreFolder>
# which represent an existing directory.
# scanPrints.awk  saves the list of files in that directory
# into an array 'printmasters'
# and then reads the output of 'ls /Volumes/Archive/WorkName/images for
# its folders
# It then prints out
# printmasters[i]
#
# Parse a series of directory listings to compare messages for error texts

function push(A,B) { A[length(A)+1] = B }
function min(a,b) { if (b > a) return a ; else return b}
function max(a,b) { if (b < a) return a ; else return b}

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
    delete printmasters[0]
    delete worksVolumes[0]
    delete pmpaths[0]
}
{

# For each
    delete printmasters
    delete worksVolumes


    saveLs($0,printmasters)

    # Get the list of volumes
    split($0,pmpaths,"/")
    work = pmpaths[length(pmpaths)-1]
    workPath = "/Volumes/Archive/"  work "/images"
    # printf("length(pmpaths)=%d\twork Path = %s work=%s\n", length(pmpaths), workPath, work)
    saveLs(workPath,worksVolumes)
    # no such thing as array bounds exception
    # print "pmlength =", length(printmasters) ,"wVlength = ", length(worksVolumes)
    longest = max(length(printmasters),length(worksVolumes))
    print $0,workPath
    for (i=0;i<longest;i++){
       printf("\t%s\t%s\n", printmasters[i],worksVolumes[i])
        }
}

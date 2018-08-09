#!/usr/bin/awk -f
#
# Parse a list of built file counts to look for a pattern
# that shows a set of bad builds.
# The pattern is that each subfolder contains the same number of files.
# The input source file is a list of directories with their file counts.
# Sample
# /Volumes/DRS_Staging/DRS/prod/batchBuilds/SomeWork1/SomeVolume1  nnnnn
#                                       .../SomeWork1/SomeVolume2  nnnnn
#                                       .../SomeWork1/SomeVolume3  nnnnn
#                                       .../SomeWork2/SomeVolume1  nnnnn
# ...
# the number of folders in the path is presumed constant
# You can double check with for f in * ; do echo -n $f ;  { ls -1 $f/image | wc -l ; } ; done


#
# Begin an error text capture cycle
function initCycle(){
    parentDir = "";
    lastBatch = thisBatch
    firstFileCount = "";
    thisfileCount = "";
    return 1
}
#
# Print pipe sep fields (text has colons)
# print ReportId, date, user, batchDirectory,Message 
function dumpCycle(inCycle) { 
    if (inCycle) {
	printf("%s|%s|%s|%s|%s|",
	       thisDate ,
	       thisReportId,
	       thisUser ,
	       thisBatchDir,
	       thisError);
	print outString;
    }
    return  0;
}

# trim leading and trailing whitespace
# Thank you Dr. Stack
# https://stackoverflow.com/questions/20600982/trim-leading-and-trailing-spaces-from-a-string-in-awk
function chop(inp){
    gsub(/^[ \t]+|[ \t]+$/,"",inp);
    return inp;
}

BEGIN {
    FS="[/ ]";
    lastBatch = ""
    dateTimesFile = "dateTimes"
    possiblyGoodFile = "possiblyGood"
    system ("rm possiblyGood")
    system ("rm dateTimes")
}
{
    batch = $7
    volume = $8
    # arbitrary number of spaces between the path and the count
    numFiles = $NF
    # print(batch,volume, $NF) # volume,numFiles)
    if (batch != lastBatch) {
        # print(batch)
	    lastBatch = batch
	    firstVolume = volume
	    firstVolumeFileCount = numFiles
	    skipToNextBatch = 0
	}
    else {

        # This block works, but sends a positive when any two subfolders of
        # batch have the same file count.
        #
#        if (numFiles == lastNumFiles) {
#          if (firstVolume != "") {
#             printf("\t%s/%s %d\n",batch,firstVolume,firstVolumeFileCount)
#             firstVolume = ""
#        }
#        printf("\t%s/%s %d\n",batch,volume,numFiles)
#        }

        # For pass 2, if you've ever seen a different file count, skip
        if (! skipToNextBatch) {
            if (numFiles == lastNumFiles) {
                if (firstVolume != "") {
                    printf("\t%s/%s %d\n",batch,firstVolume,firstVolumeFileCount)
                    firstVolume = ""
                    system("ls -ld  /Volumes/DRS_Staging/DRS/prod/batchBuilds/"  batch " >> " dateTimesFile)
                }
                printf("\t%s/%s %d\n",batch,volume,numFiles)
            }
            else
            {
                skipToNextBatch = 1
                print(batch) >> possiblyGoodFile
            }
        }

    }
    lastNumFiles = numFiles
 }

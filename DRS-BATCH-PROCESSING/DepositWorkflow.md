# Deposit workflow

## Executive Summary
* Clean up (recover) prior deposit run errors (See [Recovery.md](Recovery.md))
* Generate list of all available batches
* Filter out all uploaded batches (using downloaded results)
* Extract todays deposit file limit from batches.
## Assumptions:
### Environment
You don't need the entire drs-deposit project, just the folder DRS-BATCH-PROCESSING and its subdirectories. you might want to put those paths into your PATH, or to link them in a common dir on your path.
You will also need to link, or add to your path, the `parallelBatch` subdirectory.
#### Environment variables:
**You need these set for anything to work**
`export PR=/Volumes/DRS_Staging/DRS/prod`  This is the parent of all batch builds.
`source setBBLevel.sh` (to set `$BB_LEVEL`)
### Temporary assumptions, to change as uploads continue
Any work to deposit does not require links to it - that means (for now)
no print masters or outlines. This is taken care of in the drs-deposit/output/NoPrintNoOutline.csv
## Special circumstances
It's possible, desirable even, to re-run deposit records from prior days.
## Preparation for today's deposits

## Todays uploads
After the recovered batches are built, go into WebAdmin and download a csv of the results.
 `RemoveDepositedBatchPaths.sh` knows how to parse this for batch directory names.
### Make a new directory
`cd $DEPOSIT_ROOT`
mkdir Something. This can be anything meaningful. It could be a yyyymmdd, anything. Best to put it on the DRS_Staging
share on Druk
### Capture all the builds
`RemoveDuplicateBuilds.sh` to generate a canonical list of all builds (from `$PR/batchBuilds/`)

Ex:

```bash
j@D:drs-doc$ RemoveDuplicateVolumes.sh | tee uniqueVolumes
```
This writes a list of the volumes in the repository (Druk:/Volumes/DRS_Staging/prod/), sorts them, and removes
any duplicate builds. In the above example, it writes its output to a file `uniqueVolumes` The next processing
step uses that file.


### Remove the deposits from the list

#### Get results from DRS WebAdmin
An earlier version of the workflow used the existence of LOADREPORTS on disk to determine which works had been uploaded. This workflow uses the output of a DRS WebAdmin search. Details to follow.
** IMPORTANT ** When you do the search, be sure to add the column "Deposited in Batch with Directory" to the output columns.

![Select show/hide columns](../images/2018/04/91142cc5-2986-41f8-baaf-5133fc3e2184.png)
![Select](../images/2018/04/edd87ba9-9c7e-4159-9c76-490038b61567.png)
_Getting the 'Deposited in Batch with Name' might be helpful, but is not required_
Select these columns, and download the report into `/Volumes/DRS_Staging/DRS/KhyungUploads/$BB_LEVEL/BDRCCumulativeProdDeposits.csv`


This section is obsolete because we're using WebAdmin to download all successful results, instead of going after 
just the work that was done on the prior run.
<s>
#### Download yesterdays LOADREPORTs
In the directory you made the on the last day you uploaded,  look for the file _sourceFileList_.UploadTrack.lst. It contains a pipe separated list of users and the sources of the batches they deposited. A typical run is
```
drs2_tbrcftp|20180405DepositList1.txt
drs2_tbrcftp1|20180405DepositList2.txt
drs2_tbrcftp2|20180405DepositList3.txt
drs2_tbrcftp3|20180405DepositList4.txt
drs2_tbrcftp|20180405DepositList1.txt
drs2_tbrcftp|20180405DepositList1.txt
```
Each line decomposes into an argument list for pollDRS.sh. Use `ProcessTrackFile.sh` to turn this into a download script using `pollDRS.sh`


#### pollDRS.sh
```
Usage: pollDRS.sh uploadedBatchList remoteUser reportDir where
        uploadedBatchList       is the file list containing the list of directories.
                                        This file can be the same as the upload list (/path/to/batches/batchnnn-1)
                                        or it can be just a list of batches (BatchW.....-1)
        remoteUser              is the user on the remote system
        reportDir               is the directory which will receive the remote logs

```
It's most common use is to download the results of batches which were uploaded, and were defined in the `uploadedBatchList` parameter.

</s>

Using the output of the previous command (`uniqueVolumes`) feed that into `RemoveDepositedBatchPaths.sh uniqeVolumes outputFileName.lst`

This will give you a list in`outputFileName` (in the above example) of every batch build which still needs to be deposited.

Note that the `RemoveDuplicateBuilds.sh` output file contains more than just depositable paths.
Therefore, the sum of (depositable builds) + (already deposited builds) will be less than the
number of files in 'uniqueFiles'
### Calculate how many of these you can deposit
There's a script file, `~/drs-deposit/DRS-BATCH-PROCESSING/CountFilesInBatches.awk` which you can paste into a script, to calculate all the files in a list of batches. you can inline the script like this:
```
while read gg ; do awk ' { cmd = "find $(dirname " $1 ") -type f | wc -l"
cmd | getline thisCount
close(cmd)
sumCount += thisCount
print $1 "|" thisCount "|" sumCount }' ; done < DictUnDepositedBuildPaths.txt
```
Save that to a file, and then find the number that's before 250000 (less any repair builds you've set up earlier)
For example
`/Volumes/DRS_Staging/DRS/prod/20180402/worksList6.15.03/batchW18579-1/batch.xml|     480|242505`
Then you can just stream that out to your source file
`sed -n -e '1,/242505/p'   CumList.txt  | cut -f1 -d'|' > DoThisNow.txt`
and take it out of the original list
`sed -n '/242505/,$p' CumList.txt | cut -f1 -d'|' > AfterFirstTranchePaths.txt`
Generally, I don't re-use this index, I rebuild it every day, to allow for possible new builds
and new downloads.
### Prepare a list for ftpMultiple.sh
`DoThisNow.txt`has the full path to batch.xml files, and`ftpMultiple.sh`
only uses the batch.xml containing folder. You can either
* read DoThisNow.txt, and transform each line with basename
`while read dd ; do dirname $dd ; done <tmptmp > DoTheseNow.txt`
* Just strip out the batch.xml when you build DoThisNow.txt
`sed -n -e '1,/242505/p' -e 's/\/batch.xml//' CumList.txt  | cut -f1 -d'|' > DoThisNow.txt`
### Run ftpMultiple.sh
**Helpful to run this in a tmux window, so you can peek the status remotely.**
You won't get email notifications of success, only failure.
**DONT PEEK** There's a strong suspicion that opening an SFTP UI onto the servers degrades its performance and generates lots of spurious errors.

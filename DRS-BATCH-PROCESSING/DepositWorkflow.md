# Deposit workflow:
We do this daily before depositing.
let CODE=drs-deposit/DRS-BATCH-PROCESSING in Github
let `DEPOSIT_ROOT=/Volumes/DRS_Staging/DRS/KhyungUploads/prod/`
## Executive Summary
* Clean up (recover) prior deposit run errors
* download results from prior deposit run errors
* Generate list of all available batches 
* Filter out all uploaded batches (using downloaded results)
* Extract todays deposit file limit from batches including recovery batch file counts.
## Assumptions:
### Environment
You don't need the entire drs-deposit project, just the folder DRS-BATCH-PROCESSING and its subdirectories. you might want to put those paths into your PATH, or to link them in a common dir on your path.
You will also need to link, or add to your path, the `parallelBatch` subdirectory.
### Temporary assumptions, to change as uploads continue
Anything that's been built does not require links to it - that means (for now)
no print masters or outlines. This is taken care of in the drs-deposit/output/NoPrintNoOutline.csv
## Preparation for today's deposits
### Fix up yesterdays deposits
Correct and restart or reload any deposits you may have received. The most common problem is a duplicate upload, shown in the DRS Deposit error text:
"Object owner supplied name 'W00CHZ0103345-I1CZ43' already exists for owner code FHCL.COLL" This simply means 'W00CHZ0103345' has already been deposited.
#### Duplicate uploads
Most common problem, it means you have not downloaded a LOADREPORT of a successful batch.
This can be a little tedious, because you have to search through each user.
pollDRS.sh can help with this, as it can take batch names. It means you'll have to do a full outer join of users and batches. For example, yesterday's deposits found duplicate objects in these batches:
```
W00EGS1017555
W00EGS1017422
W00EGS1017419
W00EGS1017357
W00EGS1017352
W00EGS1017349
W00EGS1017345
W00EGS1017337
W00EGS1017341
W00CHZ0103345
```
Instead of using a UI to search each user, you can loop over `pollDRS.sh` to try the list against all users. You'll have to translate the Works into the relative batches. You can do this best by using at as a search file (`frgrep -f ...`) into the list of sources. A sample `dupScript.sh`is shown here:
```
pollDRS.sh dupBatches drs2_tbrcftp drs2_tbrcftp
pollDRS.sh dupBatches drs2_tbrcftp1 drs2_tbrcftp1
pollDRS.sh dupBatches drs2_tbrcftp2 drs2_tbrcftp2
pollDRS.sh dupBatches drs2_tbrcftp3 drs2_tbrcftp3
```
#### Why?
Because the next upload build depends on having LOADREPORTS for prior builds. (In the future, we'll use a database to drive the daily builds, not file processing.)

#### Take care of any other errors
Sometimes, you may have to go into the specific error message and rename the batch.xml.failed to batch.xml. That may help the issue go away. If it doesn't, you will have to retry the build.
After you rename the file and disconnect the DRS deposit process automatically kicks in (between 0800 and 2000 EST Monday - Friday).

** IMPORTANT DO NOT POLL FOR RESULTS RIGHT AWAY ** This can interfere with the DRS process.

### Download yesterdays loadreports
In the directory you made the prior day (see below), look for the file _sourceFileList_.UploadTrack.lst. It contains a separated list of users and the sources of the batches they deposited. A typical run is
```
drs2_tbrcftp|20180405DepositList1.txt
drs2_tbrcftp1|20180405DepositList2.txt
drs2_tbrcftp2|20180405DepositList3.txt
drs2_tbrcftp3|20180405DepositList4.txt
drs2_tbrcftp|20180405DepositList1.txt
drs2_tbrcftp|20180405DepositList1.txt
```
Each line decomposes into an argument list for pollDRS.sh. You will have to manually parse out the directories (possibly ftp1 ftp2 ftp3, or just use the user name)

### Make a new directory
`cd $DEPOSIT_ROOT`
mkdir Something. This can be anything meaningful. It could be a yyyymmdd, anything.
### Capture all the builds
`$CODE/RemoveDuplicateBuilds.sh` to generate a canonical list of all builds
(In a future, this will have deposits removed)
gives you the file `BuildList.txt`
### Remove the deposits from the list
let `DEPOSIT_ROOT=/Volumes/DRS_Staging/DRS/KhyungUploads/prod/`
this is embedded in `$CODE/RemoveDepositedBatches.sh`
This gives you a `UnDepositedBuildPaths.txt`
### Calculate how many of these you can deposit
There's a script file, `~/drs-deposit/DRS-BATCH-PROCESSING/CountFilesInBatches.awk` which you can paste into a script, to calculate all the files in a list of batches. you can inline the script like this:
```
while read gg ; do awk ' { cmd = "find $(dirname " $1 ") -type f | wc -l"
cmd | getline thisCount
close(cmd)
sumCount += thisCount
print $1 "|" thisCount "|" sumCount }' ; done < UnDepositedBuildPaths.txt
```
Save that to a file, and then find the number that's before 250000
For example
`/Volumes/DRS_Staging/DRS/prod/20180402/worksList6.15.03/batchW18579-1/batch.xml|     480|242505`
Then you can just stream that out to your source file, taking out the count metadata
`sed -n '1,/242505/p' CumList.txt  | cut -f1 -d'|' > DoThisNow.txt`
and take it out of the original list
`sed -n '/242505/,$p' CumList.txt | cut -f1 -d'|' > AfterFirstTranchePaths.txt`
(note we've stripped out the counts out of AfterFirstTranchePaths.txt)
And then run the same process on `AfterFirstTranchePaths.txt`
### Prepare a list for ftpMultiple.sh
read DoThisNow.txt, and transform each line with basename
`while read dd ; do dirname $dd ; done <tmptmp > DoTheseNow.txt`
### Run ftpMultiple.sh
You won't get notifications of success, only failure.





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

### Get all uploaded objects
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


### Get results from DRS WebAdmin
An earlier version of the workflow used the existence of LOADREPORTS on disk to determine which works had been uploaded. This workflow uses the output of a DRS WebAdmin search. Details to follow.
** IMPORTANT ** When you do the search, be sure to add the column "Deposited in Batch with Directory" to the output columns.

![Select show/hide columns](../images/2018/04/91142cc5-2986-41f8-baaf-5133fc3e2184.png)
![Select](../images/2018/04/edd87ba9-9c7e-4159-9c76-490038b61567.png)
_Getting the 'Deposited in Batch with Name' might be helpful, but is not required_
Select these columns, and download the report into `/Volumes/DRS_Staging/DRS/KhyungUploads/$BB_LEVEL/BDRCCumulativeProdDeposits.csv`


This next section is obsolete because we're using WebAdmin to download all successful results, instead of going after 
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
### Process the list
Run the command `$CODE/FindUploadableBatchPaths.sh` and tee or pipe the output. (Note the process prints
diagnostics - these are not reflected in the output)

**the script which used to do this,** `buildSendList` **is DEPRECATED**

This process creates a number of work files ending in `.lst` These are optional to keep
### Calculate how many of these you can deposit
The output of `FindUploadableBatchPaths.sh` is a pipe separated set of lines, like

`/Volumes/DRS_Staging/DRS/prod/batchBuilds/batchW10954-1-38|1093|249236`

Each record contains three fields:
- Upload path
- file count
- cumulative file count

In the following, `YourFile` is the output of `FindUploadableBatchPaths.sh`

The DRS system has a limit of 250000 files / day, so locate the line which has the largest number below that
in the third pipe field (`249236` in the example above) 


`cat YourFile | sed -n -e '1,/249236/p'     | cut -f1 -d'|' > YourUploads.lst`

### Prepare a list for ftpMultiple.sh
`YourUploads.lst`has the full path to the folders containing batches
### Run ftpMultiple.sh
**Helpful to run this in a tmux window, so you can scan the status remotely.**
You won't get email notifications of success, only failure.
**DONT PEEK using FileZilla or sftp** There's a strong suspicion that opening an 
SFTP UI onto the servers degrades its performance and generates lots of spurious errors.
**DONT PEEK** There's a strong suspicion that opening an SFTP UI onto the servers degrades its performance and generates lots of spurious errors.
## Update DRS Database
### Get recently deposited works
The DRS deposit platform maintains a database of updated objects. Various steps in the batch building process call DBApps commands which update statuses.
Periodically, should update the database with the most recent uploads. To update the
count efficiently, you should know when the last successful deposit was. When you have that date,
you run a query in HUL DRS WebAdmin to get all batches newer than that date:

![](.DepositWorkflow_images/c8260c1d.png)

The platform can handle overlap, so if you're not sure, go back further in time. It
only means that the ingest fixing takes longer to run. 

Then, update the display columns as in the getting the total cumulative step:
![Select show/hide columns](../images/2018/04/91142cc5-2986-41f8-baaf-5133fc3e2184.png)
![Select](../images/2018/04/edd87ba9-9c7e-4159-9c76-490038b61567.png)

Download that file. **Do not save it as the `BDRCCumulativeFile...` as in the other step.
It is only a differential file, not the cumulative one.**
## Run DRSUpdate


Give the usual config information and the name of the file you saved in the previous step:
```bash
(py371) gre@Shmeng:Downloads$ DRSUpdate -d prod:~/.garTweezix.config DRSDepositsPost2018-10-17.csv
/Users/gre/pyEnvs/py371/lib/python3.7/site-packages/pymysql/cursors.py:276: Warning: (1265, "Data truncated for column 'IngestDate' at row 1")
  self._query(q)
 50 calls ( 6.39 %).  Rate: 11.21 /sec
 100 calls ( 12.79 %).  Rate: 11.26 /sec
 150 calls ( 19.18 %).  Rate: 11.23 /sec
 200 calls ( 25.58 %).  Rate: 11.26 /sec
 250 calls ( 31.97 %).  Rate: 11.28 /sec
 300 calls ( 38.36 %).  Rate: 11.23 /sec
 350 calls ( 44.76 %).  Rate: 11.30 /sec
 400 calls ( 51.15 %).  Rate: 11.26 /sec
 450 calls ( 57.54 %).  Rate: 11.16 /sec
 500 calls ( 63.94 %).  Rate: 11.24 /sec
 550 calls ( 70.33 %).  Rate: 11.29 /sec
 600 calls ( 76.73 %).  Rate: 11.23 /sec
 650 calls ( 83.12 %).  Rate: 11.29 /sec
 700 calls ( 89.51 %).  Rate: 11.26 /sec
 750 calls ( 95.91 %).  Rate: 11.29 /sec

```




# Deposit workflow

## Executive Summary
* Clean up (recover) prior deposit run errors (See [Recovery.md](Recovery.md))
* Generate list of all available batches
* Filter out all uploaded batches (using downloaded results)
* Extract todays deposit file limit from batches.
## Assumptions:
### Environment
You don't need the entire drs-deposit project in your path. See the directory DRS-BATCH-PROCESSING/deployment/ `copyLinksToBin` and `makeLinks`.
You can use them to update files in your `~/bin` folder with current GIT objects.
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


### Get results from DRS WebAdmin
An earlier version of the workflow used the existence of LOADREPORTS on disk to determine which works had been uploaded. This workflow uses the output of a DRS WebAdmin search. Details to follow.
** IMPORTANT ** When you do the search, be sure to add the column "Deposited in Batch with Directory" to the output columns.

![Select show/hide columns](../images/2018/04/91142cc5-2986-41f8-baaf-5133fc3e2184.png)
![Select](../images/2018/04/edd87ba9-9c7e-4159-9c76-490038b61567.png)
_Getting the 'Deposited in Batch with Name' might be helpful, but is not required_
Select these columns, and download the report into `/Volumes/DRS_Staging/DRS/KhyungUploads/$BB_LEVEL/BDRCCumulativeProdDeposits.csv`

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

# Recovery from deposit errors
## Platform
## Software
You will need the complete contents of `github/drs-deposit/DRS-BATCH-PROCESSING` It can be useful to create symbolic links
in ~/bin, or somewhere else in your path, to these. If you are not a developer, see AO for setting up your machine. 
### Cisco AnyConnect
Launch the Cisco AnyConnect VPN to vpn.harvard.edu. Setting this up is **way** beyond the scope of this doc. You can only connect to DRS deposit servers when this is running.
### Email notification
The default `project.conf` has settings which email `jimk@tbrc.org` when a batch deposit fails.
a user needs to manually extract the mail messages. The preferred workflow is to
+ select all the email messages (you can use a filter 'DRS Deposit Error') (See **Collecting errors:** `mailerrs.dat` for details) 
+ Save them into one file, in the deposit directory (typically `/Volumes/DRS_Staging/DRS/KhyungUploads/yyyymmdd/mailerrs.dat`. The filename `mailerrs.dat` is required)
+ Run the recovery scripts detailed below, **in order**
### Deposit directory
In the rest of this document, carry out these instructions in the **deposit directory.**
The deposit directory must contain the list of paths which contain the batch directories contained in the
mail message.
This example uses `/Volumes/DRS_Deposit/DRS/KhyungUploads/prod/2018/06/01/` as the deposit directory.

 
## Recovery scripts
1. First, run `autoRecovery`
This script parses the `mailerrs.txt` you saved above. It creates `mailErrs.dat` and then launches into recovery.
It examines each error message, and decides whether to:
- Delete already deposited batches by invoking BuildDeepDeleteList.sh
- Fix failed deposits by replacing `descriptor.xml` by BuildRecoveryList.sh
It then calls `RunSerialFtp` to execute the fix for each error.

**autoRecovery Usage**
`autoRecovery` takes two arguments:
 - the UploadTrack list (derived from the output of `ftpMultiple.sh`) 
 - a double quoted file specification which describes all the batches which were uploaded. Note that the internal `splitWorks.sh` script
 not only splits the works into the number of FTP Users baseName[1-4].txt, but leaves the original file in baseName5.txt.You can use baseName5.txt as the one, unquoted argument here, instead of a bash file specification 
        
# Oh, ROB (Sob)
`autoRecovery` works by 
+ replacing `descriptor.xml` files from the batch build directory (because the DRS deposit system overwrites, thereby breaking the 
Checksum which BatchBuilder wrote into its batch.xm)
+ replacing the `batch.xml` with the original source
+ disconnecting
This launches DRS deposit on the server, which will retry the deposit (in the DRS deposit service window, 0800 - 2000 M - Fri).
Sometimes this will fail again. In this case, there is not much value in replacing these.
To remove these failed builds from the DRS Server,
1. Collect the error messages from you mail system as described above. Save the into **a new version of** `mailerrs.txt`
** Be sure not to use the existing one - this proces is destructuive.
1. Run `autoRecovery -D` This uses the `mailerrs.txt` file to drive the deletion process.

## Recovery prior to daily builds

### Fix up yesterdays deposits
Correct and restart or reload any deposits you may have received.
You can use the existence of a downloaded `batch.xml.failed` to infer a deposit error, but it is by no means certain (a deposit directory can have both LOADREPORT and `batch.xml.failed` files). As well, the downloaded files do not tell you the error. You have to examine the drs deposit failure emails. I fselect all the error messages in the Mac into one file )
### Collecting errors: `mailerrs.dat` 
I collect and parse the emails on the build machine. 
+ In the MacOS mail client, select all the error messages.
+ File --> Save As into a plain text file. In this example, `mailerrs.txt`
+ Process the file through a script (`~/bin/parseMail.awk`) `cat mailerrs.txt | parseMail.awk > mailerrs.dat`
This gives a data file.Typical format: 
```
April 26, 2018 at 9:02:35 AM EDT|1524747755529114845|drs2_tbrcftp3|batchW23945-1|Caught exception in ingest(): javax.persistence.PersistenceException: org.hibernate.exception.GenericJDBCException: Could not open connection|
April 26, 2018 at 9:02:25 AM EDT|1524747745829114833|drs2_tbrcftp3|batchW23947-1|Caught exception in ingest(): javax.persistence.PersistenceException: org.hibernate.exception.GenericJDBCException: could not extract ResultSet|
```
For the rest of this tutorial, this file is named `mailerrs.dat`

#### Mapping errors to batches
For example, the error mail message contains a line: 
`
Batch Directory: batchW20813-5
`
There must be a reference in a list of batch build paths to this directory.
These files are typcially named `buildList[1-n].txt`
In this example,  you can use `buildList2.txt`
It contains the batch build path 
`buildList2.txt:/Volumes/DRS_Staging/DRS/prod/20180515/worksList3.23.25/batchW20813-5`

### AutoRecovery
This is what `autoRecoveryCore` shell does
In the mail error data file, separate out the records which contain these three strings, as they each have different workflows to repair:
* 'Object owner supplied name' - this means the object exists. ("Duplicate deposit")
* ' Could not create PROCESSING .. because directory is unwritable' - this is a more serious error fixed with the "DRS permissions" workflow.
* Any other error text is the "Everything else" workflow.

There are three distinct workflows for errors

[^88fae8cf]: My experience has been that this is best done on a MacOS mail client. On Windows, doing this and ftp'ing it has \n side effects.

Error Type|Error Text|Fix type
----|-----|------
Duplicate deposit|'Object Owner supplied name exists'|[workflow]('Object Owner supplied name exists')
DRS permissions failure  |'Could not create PROCESSING'|Inhibit further PROCESSING
Everything else|varies|recover the batch using workflow ???? below
  |   |  
### Error resolution workflows
#### Workflow 'Object Owner supplied name exists'
Fix these first. When you download batch results, you don't want these in your downloads. These occur because of absences in the deposit records. Go to WebAdmin and refresh the deposit batches.


There are two possible causes for this error:
- the entire batch has been already deposited
- the volume (same text as the OSN) was deposited in a different batch.

To troubleshoot:
Here's a typical example of a duplicate OSN Message. Data you will need is marked with `==>`:

```
Report ID: 1594867901370100398
==>Drop Box: drs2_tbrcftp3

==> Batch Directory: batchW1KG13126-6-5d

Batch Name: FHCL.COLL_batchW1KG13126-6-5d_20200520_125333

An unexpected problem occurred processing batch . If this problem persists, please contact https://nrs.harvard.edu/urn-3:hul.ois:drshelp, forwarding the entire contents of this message.

Message: 

Object owner supplied name ==> 'W1KG13126-I1KG13275' already exists for owner code FHCL.COLL
```
##### Was the complete batch uploaded already?
To see if the entire batch has been already deposited, look for the **Batch Directory** in BDRCCumulative....csv
`grep 'batchW1KG13126-6-5d' $PR/../KhyungUploads/prod/BDRCCum*csv`
If you get returns, then look for the specific volume:
`grep 'W1KG13126-I1KG13275.*batchW1KG13126-6-5d' $PR/../KhyungUploads/prod/BDRCCum*csv`
if that returns, then you are most likely all set. Just delete the batch directory.
sftp to the `==> Drop Box` directory and delete the /incoming/batchW.... folder that reported the error. In the following 
example:
```
Report ID: 1594912498895100485
Drop Box: drs2_tbrcftp2
Batch Directory: batchW1KG10687-1-93
Batch Name: FHCL.COLL_batchW1KG10687-1-93_20200514_160846

An unexpected problem occurred processing batch . If this problem persists, please contact https://nrs.harvard.edu/urn-3:hul.ois:drshelp, forwarding the entire contents of this message.

Message: 
Object owner supplied name 'W1KG10687-I1KG10689' already exists for owner code FHCL.COLL
```
 sfp to drs2_tbrcftp2 and delete /incoming/batchW1KG10687-1-93/ This is a tedious process
 which is facilitated in 'FileZilla Pro' - it recursively travels the directory and deletes.
 ##### Was the volume deposited already in a different batch?
 If so, you have to examine the batch to see if any other volumes in the batch which failed were already deposited.
 In this example, only one work in the batch was found to be duplicate:
 
```
Report ID: 1594867901370100398
==>Drop Box: drs2_tbrcftp3

==> Batch Directory: batchW1KG13126-6-5d

Batch Name: FHCL.COLL_batchW1KG13126-6-5d_20200520_125333

An unexpected problem occurred processing batch . If this problem persists, please contact https://nrs.harvard.edu/urn-3:hul.ois:drshelp, forwarding the entire contents of this message.

Message: 

Object owner supplied name ==> 'W1KG13126-I1KG13275' already exists for owner code FHCL.COLL
```
- Look for batchW1KG13126-6-5d in BDRCCum...
```shell script
xxxups$ grep  batchW1KG13126-6-5d !$
grep  batchW1KG13126-6-5d /Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCum*csv
xxxups$
```
Not there. So which batch was it deposited in?
```shell script
xxxups$ grep  W1KG13126-I1KG13275 /Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCum*csv
/Volumes/DRS_Staging/DRS/KhyungUploads/prod/BDRCCumulativeProdDeposits.csv:484289538,
W1KG13126-I1KG13275,"URN-3:FHCL:100002474, URN-3:HUL.DRS.OBJECT:100002473",
Buddhist Digital Resource Center,FHCL.COLL,FHCL.COLL.TBRC_0001,PDS DOCUMENT,,
==>batchW1KG13126-4-17,<==
993052,2020-07-15T20:55:58.0Z,FHCL.COLL_batchW1KG13126-4-17_20200520_123820,737,,R,"bstan 'gyur/ (pe cing /), pe cing bstan 'gyur, bstan 'gyur/ (pe cin/), pe cin bstan 'gyur, བསྟན་འགྱུར། ༼པེ་ཅིང་།༽",Tibetan Buddhist Resource Center,316010256
xxxups$
```
Here we see the volume's been published, but in a different batch,`batchW1KG13126-4-17`
(column 10)
So we have to look at both batches:
- if they contain the same volumes, then delete the batch with the error.
- if they have different volumes, then you have to resolve each one.
In the above case, the batch reporting the error has a super set of the volumes in the other batch.
This will require you to roll back the DRS for the undeposited volumes.











**Note: the directory could have both a batch.xml.failed and a LOADREPORT. If it has a LOADREPORT, just delete the batch.xml.failed and the other directory (Wnnnnn-Immmmmm)**
#### Workflow Inhibit further PROCESSING
The first two steps are the same as the above workflow.
+ Next ** VERY IMPORTANT ** Email drs-support with the report ids (in `mailerrs.dat`) output. They will address the underlying problem and will let you know when these directories can be reset to build. In the meantime, you have to inhibit the build retries.
+ Group these into files of batches, one file for each user.
+ Process these through ` FixUnwritableRemotePath.sh`
```
Usage: FixUnwritableRemotePath.sh remoteUser
where
        remoteUser  is the user on the remote system who owns the files.
        list of remote directories is read from input
```
Since this process responds to a fire, it immediately runs `sftp` to change each directory's `batch.xml` to `batch.xml.wait` This prevents DRS from ingesting them. Once DRS has done this, you run `ResetUnwritableDirectories.sh` (same arguments) to set them ready to be ingested.
#### Have any errors been resolved?
+ Determine what's been published. `/Volumes/DRS_Staging/DRS/KhyungUploads/$BB_LEVEL/BDRCCumulativeProdDeposits.csv` keeps a running total of what we've deposited. `cut -f12 -d, | sort -u` to get the list of batches (you need the unique because a work can span deposits) (Nerd note: although the batch directory name is heading 9, one of the data fields has a , in it.)
+ Derive the errored batches `grep 'Batch Directory' ` _all your error files_
This gives the batch ids of the failures. `sort -u` to filter out duplicates.
From the repository, get all the batch ids of what's deposited.

#### Everything else
These are transient exceptions caused by DRS ingest failures. The fix is to use
`autoRecovery`
```
jimk@vpn-59-107:20180425$ BuildRecoveryList -h
        synopsis: BuildRecoveryList -h  this message
        synopsis: BuildRecoveryList  -o outdir -p prefix -s srcs datafile

        where:
                -o      is the destination directory for sets of sftp scripts
                -p      is the prefix for sftp scripts
                -s      ARG_SRCS is the filespec for a set of files which is parsed to locate Built 
                        batches. Metachars must be quoted (e.g. frelm*.txt)
                dataFile is a list of batch names, one per line.
```
`BuildRecoveryList` creates a directory of sftp scripts whose names are prefixed with the prefix. These batch scripts recover a failed build correctly by uploading all the "descriptor.xml" files in the batch, and then, finally, the batch.xml file. This awkward process is needed because the DRS process modifies descriptor files during the ingestion process. When it fails, if you only rename or upload batch.xml, you get the MD5 checksum error (batch.xml contains checksums for its descriptor.xml files, and the checksums won't match after DRS has changed the descriptor files).
Build one set of recovery scripts for each user.
+ Run each set of scripts through `RunSerialFtp.sh`
```
Usage: RunSerialFtp.sh scriptDirectory remoteUser 
where:
        scriptDirectory contains one or more sftp batch scripts
	remoteUser is the user account on the remote system
```
The scripts you generated in the previous step reset the batches for rebuild. The DRS ingestion process restarts immediately

** IMPORTANT DO NOT POLL FOR RESULTS RIGHT AWAY ** This can interfere with the DRS process. It requires
about two minutes to process each error, so go away and do something else for the required time.

## When recovery is not possible
Sometimes, works fail ingest repeatedly. You may want t forget they've been built, and rebuild them from scratch.
This is a two step process:

1. Removing the deposited batches from the DRS dropbox, and removing the built batches from the build file folder. `autoRecovery` does this when you
answer 'yes' to the `Retry or Delete` prompt.
2. Removing the build status from the DRS database (BDRC database which tracks DRS builds - not affiliated with the
DRS dropbox).  `delete-batches.sh` was written to handle this case. **Syntax:** `delete-batches.sh <upload-track-file> <build-list-spec>`
This step erases all the records of the volumes in the batch build folder from every having been built, so that it is
eligible for building again when the `getReadyWorks` script is run again.


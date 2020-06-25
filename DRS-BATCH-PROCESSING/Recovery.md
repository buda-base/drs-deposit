# Recovery from deposit errors
## Platform
## Software
You will need the complete contents of `github/drs-deposit/DRS-BATCH-PROCESSING` It can be useful to create symbolic links
in ~/bin to these, 
### Cisco AnyConnect
Launch the Cisco AnyConnect VPN to vpn.harvard.edu. Setting this up is **way** beyond the scope of this doc. You can only connect to DRS deposit servers when this is running.
### Email notification
The default `project.conf` has settings which email `jimk@tbrc.org` when a batch deposit fails.
a user needs to manually extract the mail messages. The preferred workflow is to
+ select all the email messages (you can use a filter 'DRS Deposit Error')
+ Save them into one file, in the deposit directory (typically `/Volumes/DRS_Staging/DRS/KhyungUploads/yyyymmdd/mailerrs.dat`. The filename `mailerrs.dat` is required)
+ Run the recovery scripts detailed below, **in order**
### Deposit directory
In the rest of this document, carry out these instructions in the **deposit directory.**
The deposit directory must contain the list of paths which contain the batch directories contained in the
mail message.
This example uses `/Volumes/DRS_Deposit/DRS/KhyungUploads/prod/2018/06/01/` as the deposit directory.

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
 
## Recovery scripts
1. First, run `autoRecovery`
This script parses the `mailerrs.txt` you saved above. It creates `mailErrs.dat` and then launches into recovery.
It examines each error message, and decides whether to:
- Delete already deposited batches by invoking BuildDeepDeleteList.sh
- Fix failed deposits by replacing `descriptor.xml` by BuildRecoveryList.sh
It then calls `RunSerialFtp` to execute the fix for each error
        
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
The fix is to go into an SFTP UI (FileZilla or  BitVise), and delete the directory in the UI. This is a very tedious and slow procedure.

3. For each user, open an SFTP ui and delete `/incoming/batchWnnnnn-m`

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

** IMPORTANT DO NOT POLL FOR RESULTS RIGHT AWAY ** This can interfere with the DRS process.

It requires about two minutes to process each error, so go away and do something else for the required time.


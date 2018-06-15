#Recovery from deposit errors
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
In the rest of this document, the deposit directory, from which all 
The deposit directory must contain the list of paths which contain the batch directories contained in the
mail message.
This example uses `/Volumes/DRS_Deposit/DRS/KhyungUploads/prod/20180601` as the deposit directory.
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
1. Delete already deposited batches
The workflow to recover from duplicate uploads is:
    + cd `deposit directory`
    + invoke `deleteAlreadyDepositedSFTP.sh` This creates and invokes sftp scripts which clean up after attempts to deposit a volume which has already been deposited.
    These scripts are lengthy, so they run in the background. This command requires that `mailerrs.dat` exists.
    
# Oh, ROB (Sob)
`autoRecovery` works by 
+ replacing `descriptor.xml` files from the batch build directory (becausethe DRS deposit system overwrites, thereby breaking the 
Checksum which BatchBuilder wrote into its batch.xm)
+ replacing the `batch.xml` with the original source
+ disconnecting
This launches DRS deposit on the server, which will retry the deposit (in the DRS deposit service window, 0800 - 2000 M - Fri).
Sometimes this will fail again. In this case, there is not much value in replacing these.
To remove these failed builds from the DRS Server,
1. Collect the error messages from you mail system as described above. Save the into **a new version of** `mailerrs.txt`
** Be sure not to use the existing one - this proces is destructuive.
1. Run `autoRecovery -D` This uses the `mailerrs.txt` file to drive the deletion process.

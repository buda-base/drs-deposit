# drs-deposit

Harvard DRS Deposit base

# Daily Workflow

Note this is a high level summary, at the checklist level. It does not describe details of installation and operations.

For details and design documents, please see

* [Deposit Workflow](src/DepositWorkflow.md)
* [DR Design Doc](./src/DRDesignOverview.md)
* [Batch Building](./src/BatchBuilding.md)
* [Parallel Batching](./src/parallelBatching.md)

## Platform Requirements

+ The BatchBuilding platform. Platform requires:
    - Python 3.6+ in a virtual environment
    - Bash v4+
    - drs-deposit github - only needs src folder, not complete repository
    - drs-deposit/DBApps installed (see [DBApps Readme](DBapps/README.md) )
    - install from src/deployment/copyLinksToBin
    - installed BatchBuilder (see [Installing HUL BatchBuilder](#installing-hul-batchbuilder))

+ Khyung: Uploading platform. Requires:
    - Python 3.6 (recommended in a virtual environment). See [^Detailed platform Requirements]
    - DBApps as above.
    - Cisco VirtualConnect software (from Harvard)
+ Optional: another machine with Cisco AnyConnect software

Except for downloading the CSVs, and the step of collecting the error results, all these steps are command line, so you
can run them through `ssh`. I advise you run them under `tmux`, so that long running commands don't pin down your
machine.

## Detailed platform requirements

1. OS:This suite has been tested on:

- MacOS
    - High Sierra
    - Mojave
    - Catalina
- Debian
    - 9
    - 10

1. Coreutils (MacOS only).  `brew install coreutils` ( as root, or owner of `/usr/local/bin`). Be sure
   to `brew list coreutils` and read the caveat about PATH. These scripts expect the GNU versions of their commands.
1. Python 3.7 and virtualenv. Since we can't use Python 3 at a systemwide level on MacOS machines, each user has to
   create a virtual env and initialize it. See [python venv documentation](https://docs.python.org/3/library/venv.html).
   If `pip` breaks, you need to drop back your openssl to version
   1.0.2a (`brew remove --ignore-dependencies openssl && brew install openssl=1.0.2a` or something like it.)
    1. The python scripts depend on pip packages `lxml` and `pymysql` which should be automatically installed with the
       pyPI (see [DBApps Readme](DBApps/README.md)
1. Harvard University Library Batch building system. See [Installing HUL BatchBuilder](#installing-hul-batchbuilder)

### Installing HUL BatchBuilder

#### Download and Install

See [DRS Installation and Setup](https://wiki.harvard.edu/confluence/display/LibraryStaffDoc/1.+Installation+and+Setup)

#### configure environment and customize
With release 2.4.1 of Batchbuilder, there is no customization needed.

##### DRS customizations in source code

BatchBuilder 2.3 and earlier have a `fits` configuration that doesn't work for us. We created `
BatchBuilderPre23LocalModes/fits/xml/fits.xml. But in 2.4.1 and later, this is not needed.

Also, the customizations in `batchbuildercli.sh` are optional - they are for logging only

## Steps

** HYPER IMPORTANT **
Make sure that your QA/Production levels are synchronized.

Legend:
BB_bin: the directory where you installed BatchBuilder (e.g. `~/bin/BatchBuilder-2.4.1`)
For details on WebAdmin connection and usage, see [HUL DRS Wiki Connecting to WebAdmin](https://wiki.harvard.edu/confluence/display/LibraryStaffDoc/1.+Connecting+to+Web+Admin)

| Level      | BatchBuilderAction                                     | Environment       | BDRC DB Connection                                   |WebAdmin UI|
|------------|--------------------------------------------------------|-------------------|------------------------------------------------------|---|
| Production | $BB_bin/conf/bb.properties contains bb.properties.prod | set BB_Level=prod | `prod:~/.d...` (some scripts set this from BB_Level) |http://nrs.harvard.edu/urn-3:hul:drs2-admin|
| QA         | $BB_bin/conf/bb.properties contains bb.properties.qa   | set BB_Level=qa   | qa:~/.d...                           |https://nrs.harvard.edu/URN-3:HUL:DRS2QA-ADMIN|

| Host     | Action                                                                                                                                                                                          | Comments                                                                                                                                                                                                                                                                                                                                                                                       |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Any PC   | Get Deposit Updates                                                                                                                                                                             | Log on to the Harvard VPN. Point a browser to [WebAdminSearch][68fcc779]                                                                                                                                                                                                                                                                                                                       |
|          | Get all deposits to date                                                                                                                                                                        |                                                                                                                                                                                                                                                                                                                                                                                                |
|          |                                                                                                                                                                                                 | Search for Objects. In the URL, if you don't see the + button (![The Plus button](images/2018/06/the-plus-button.png)) Click the 'Reset' button                                                                                                                                                                                                                                                | |     
|          | Search for objects with this billing code ![Billing code HFCL.COLL.TBRC_0001](images/2018/06/billing-code-hfcl-coll-tbrc-0001.png)                                                              |                                                                                                                                                                                                                                                                                                                                                                                                |
|          | Select  Action 'show/hide columns' ![Show Hide Columns](images/2018/06/show-hide-columns.png)                                                                                                   |                                                                                                                                                                                                                                                                                                                                                                                                |
|          | Add 'Insertion Date' 'Deposited in Batch With {Directory, ID, LoadDate, Name}' ![Select 'Show'](images/2018/06/select-show.png)                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                |
|          | Select Action 'download search results.'                                                                                                                                                        |
|          | Save to your drs-deposit working directory output/BDRCCumulativeProdDeposits.csv                                                                                                                |
|          | Get last period's deposits                                                                                                                                                                      | Run another search, looking for only the incremental change. See `~/drs-deposit/output/DepositUpdates` and figure out the latest deposit date You will have to look in the newest file to look at the latest Insertion date(not _createDate_). The date picker's basis starts at midnight, so if you pick 28 June in the calendar, you are getting everything newer than 28 June 00:00:00 Zulu |
|          | **If you are doing this in the same browser session, you will get the same columns you did before. If you have left the WebAdminSearch site, and returned, select Hide/Show columns as above.** |
|          | Don't worry if your incremental files contain overlapping dates: the DRS database can cope. Better than missing dates.                                                                          |
|          | Commit and Push                                                                                                                                                                                 | Make these changes available to other machines.                                                                                                                                                                                                                                                                                                                                                |  
| **Druk** | Update the DRS database                                                                                                                                                                         | Any PC with the Python library installed, and the DRS Db dbConfig files, could do this, but because of the DRS database restrictions on remote access, this is best done on a machine in the BDRC network. If that machine is in the HUL VPN, that also works.                                                                                                                                 |  
|          | Create a work area [^b4db8524]                                                                                                                                                                  | I use `Druk:~jimk/runs/prod/yyyy/mm/dd`  The process is location independent, but must have access to the `Khyung:DRS_Staging` share, and must declare an environment variable `$PR=/Volumes/DRS_Staging/DRS/prod`                                                                                                                                                                             |
|          | Get the next ready works                                                                                                                                                                        | Run the command `DRSUpdate -d prod:~/.drsBatch.dbConfig <location you saved the incremental file ...drs-deposit/output/DailyUpdates/whatveverfile`. This updates the database with the latest builds, so that getting the next tranche of files to build can proceed.                                                                                                                          |
|          | Make sure the last batch building run completed.                                                                                                                                                | Don't worry about failures. There's a separate workflow coming for batchBuild failures                                                                                                                                                                                                                                                                                                         |
|          | Get the next round of ready files                                                                                                                                                               | Run the python script `getReadyWorks -d prod:~/.drsBatch.dbConfig -n <someNumber> <someFilePath>`  It turns out we can build about 500 batches in a day, using three streams, so `-n 500` is reasonable. **Warning: this process is slow, and is a memory pig.** You can do this serially to `-n 100 someFilePath[1...n]` and then cat `someFilePath[1..n]` together.                          |
|          | Prepare to run                                                                                                                                                                                  | Figure out how many parallel executions you want to run. 4 is a useful upper limit (we've seen that, after 3 parallels, the 4th, 5th, and later streams get starved for CPU)                                                                                                                                                                                                                   |
|          | Split the readylist into the number of streams  `splitWorks -n 3`**This is not** `splitWorks.sh`                                                                                                |                                                                                                                                                                                                                                                                                                                                                                                                | 
|          | Off with his head!                                                                                                                                                                              | Start a tmux session. This runs for a long time, and you dont want to depend on your console access.                                                                                                                                                                                                                                                                                           |
|          | And go                                                                                                                                                                                          | Launch `runAny.sh filespecOfYourSplitWorks output'` for example: `runAny.sh myBuildCandidates[1-3].txt` `runAny.sh` spawns many background processes (one per file in its arguments list), and then exits. No advantage to running it in the background.                                                                                                                                       |
|          | Checking status                                                                                                                                                                                 | In the same working directory, examine the `timin/underway` and `timing/finishedRuns` directory.                                                                                                                                                                                                                                                                                               |

[68fcc779]: http://nrs.harvard.edu/urn-3:hul:drs2-admin "Harvard Web Admin Search"
[^b4db8524]: Details of the following section are in: [Building Batches][65e185e8]

[65e185e8]: ./src/BatchBuilding.md "Building Batches"

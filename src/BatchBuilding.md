# Batch Building
## Document Version
0.2,  13 June 2018
## Getting list of works
### SQL Structures
* `AllReadyWorks`: works which have no printmasters or outlines
* `ReadyWorksNeedsBuilding`: subset of `AllReadyWorks` which have not been deposited
Technically, these return collections of __Volumes__ which have not been deposited.

### Workflow
#### Prerequisites to these steps:
1. Make sure you have updated the DRS db with the latest results from WebAdmin.
See Technical Reference, ????

#### Build a list of items to batch build
You need to do this every time you start, to make sure you are not building anything that has been built or deposited.

Before running this be sure to check that you have Python 3.6 and the DBApps scripts set up. DBApps installation is in [README](./DBApps/README.md) document in DBApps.

**Run**: `getReadyWorks -d prod:~/.drsBatch.config -n 200 ./yyyymmddReadyWorks`

`-d` Should be your batch config file. The recommended location is in you home directory

`-n` the total number of works you want to batch build. The script defaults to n = 200
__WARNING__ This process is slow - approximately 1 minute per 10 works.

your need to create a valid filename for the output file. We recommend a name with the date in yyyy-mm-dd format

**Results**:a file named `yymmddReadyWorks` in the output folder

#### Split the ready works
**Run:** `splitWorks fileName -n` where -n is the number of instances you want to run. For `fileName` use the output of `getReadyWorks.py`
**Results**: fileName1....fileNameN
#### Build the batches
Entry point is `runDRS.sh` which processes the files.
Typically you'd run it against the splitworks, by using file globbing:
`./runDRS.sh filename[1-n]` where the list is the output of the file you listed
**NOTE:** Don't include the master source file in your argument list. The platform won't know that you're asking it to batch build the same works twice.

Usage:
```
$ ./runDRS.sh -h
                synopsis: runDRS.sh [-h] file1,file2,...
                -h: shows this message
                run multiple lists of works given in 'files'
                in parallel execution, One process per file
```

+ Grab a cuppa (or 10) while your batch building proceeds.

#### Test for done
The process writes statuses in `timing/underway` and `timing/finishedRuns`
When `timing/underway` has no more files in it, and `timing/finishedRuns` has one file for each input file to `runAny.sh` the process is complete.
You can run `topStats.sh` in the meantime. If you see java processes somewhere in the list, things are proceeding ok. Make multiple observations.

#### Contents of timing files
In Underway, the file contains the process id of the batch build for the file, and the start time.
eg `24004_14:40:36`
In finishedRuns, the underway is suffixed with the result and the finish time:
eg: `24004_14:40:36_0_19:27:01` The 0 means the batch building process succeeded, and finished at 19:27. **The process succeeding does not mean every batch build succeeded.** Batch builds fail all the time, but the process continues.
## Technical reference
### Python routines
#### `drs-deposit/DBApps/src` contains:
`getReadyWorks.py` which collects all the works which need to be built (in rev. 1, these are just works which have not been deposited), and downloads them into a csv file whose bnf looks like:
```
{
    {
        {headerline}
        {dataLine}+
    }
}
```

Example:
```
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00EGS1017169,14253976,W00EGS1017169-I00EGS1017171,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00JR625,15325049,W00JR625-I2PD19927,,
W00JR625,15325049,W00JR625-I2PD19928,,
W00JR625,15325049,W00JR625-I2PD19929,,
W00JR625,15325049,W00JR625-I2PD19930,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00KG015,15325052,W00KG015-I1KG22767,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00KG017,15325058,W00KG017-I1CZ105,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00KG02762,15325075,W00KG02762-I1KG23320,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00KG03797,14254417,W00KG03797-I00KG03832,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00KG0541,15327210,W00KG0541-I1KG20953,,
WorkName,HOLLIS,Volume,OutlineOSN,PrintMasterOSN
W00KG0544,15325090,W00KG0544-I1KG23076,,
```

#### `splitWorks.py`
Breaks the file above into `n` files where each file contains roughly the same number of
``` {
        {headerline}
        {dataLine}+
    }
```
sets.
Resulting files are named after the first file, which the suffix 1 in the filename
(the file extension is preserved)

Example
```
splitWorks -n 4 somefile.txt

somefile1.txt
somefile2.txt
somefile3.txt
somefile4.txt
```

# Batch Building
## Document Version
0.1,  13 June 2018
## Getting list of works
### SQL Structures
* `AllReadyWorks`: works which have no printmasters or outlines
* `ReadyWorksNeedsBuilding`: subset of `AllReadyWorks` which have not been deposited
Tehcnically, these return collections of __Volumes__ which have not been deposited.

### Python routines
####`drs-deposit/DBApps/src` contains:
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


### Shell scripts
Entry point is `runMultiple.sh` which processes the files.

Usage: 
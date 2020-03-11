# Parallel Batching
This folder contains scripts which implement parallel batch building and the tools used to monitor the processes.
## Overview
Parallel batching has three major phases:
* Dividing the set of works into lists.
* Launching the batches in Parallel
* Monitoring the ongoing works
* Analyzing errors

These scripts can be run from any location. It's advisable to copy them out of the repository, so that works lists & etc aren't added to Git. (unless that's the goal, which is somewhat fishy from a Don't Repeat Yourself perspective)

These scripts use nothing from the environment. Input and output folder locations are either passed from one layer to another, or are user-edited at the top of each script.

## Step 1: Setup
The setup process is summarized in this image (This is a static image of [Batching Part 1 gdrawing][2f8f924c])
![Batching part 1](../images/2018/01/Parallel%20Batching%201.png)

  [2f8f924c]: https://drive.google.com/open?id=1v21PO7yinmvW4j298s_xsSJ1HYi2K5BQcWs-5JRdMUQ "Batching Part 1"

**`splitWorks.sh`**

Given a file which contains a list of works, separate it into files of 240 works each. You have to know where the master list of works is. Edit the script itself to change the number of lines in a file.

It's advisable to run this in a subdirectory, to not clutter up your working directory.

### Step 2:Launch `runAny.sh`

** Location Note ** These scripts don't need to be run from any particular directory  Paths to other scripts are fully qualified in the calling script. These may need configuration in your particular view.

`runAny.sh` is called with the beginning and end numbers of a sequence
(e.g. `runAny.sh 3 6`) which sets up a call to the `makeOneDrs.sh`script.
the beginning and end numbers are the numeric part of the worksList_nnn_.txt file name.

Along the way, it initializes the directories for tracking progress, passing their paths to `makeOneDrs.sh`

Note that the parallelism happens here. `runAny.sh` spawns one child thread for each work list.

## Step 3: Batching
The batching process is described in [Parallel Batching 2 gdrawing][8d428e13], and is shown in ![Batching 2 flowchart](../images/2018/01/Parallel%20Batching%202.png)

Note in the `makeOneDrs.sh` processing, that it invokes `make-drs-batch.sh` in the background, so that it can capture its pid for logging purposes. After it launches `make-drs-batch.sh` it sits and waits for it to exit.

At this writing, each `make-drs-batch.sh` processes 240 works. Depending on how many run simultaneously, this step can take hours to days.

  [8d428e13]: https://drive.google.com/open?id=1pOOTwafDiVma8hftYcQQ0aJbTPIvI6hLgtSkR4zHVrM "Parallel Batching 2"

## Step 4: Monitoring
**Location Note** Most of these scripts were written as utilities, and use resources, such as magic file names and directory paths. These resources are catalogued below
The most important of these are:

resource|defined in (file:variable)|purpose
--|---|--
underway|`runAny.sh:underwayDir`|Location of status files for underway  
finished|`runAny.sh:underwayDir`|Location of status files when jobs are completed.
Works source|`makeOneDrs.sh:WORKS_SRC`|Location of worksList*n*.txt files  
Batch output|`makeOneDrs.sh:BATCH_OUTPUT_HOME`|Parent directory of all completed batch projects.

Before monitoring works, be sure these scripts point to the correct directories.

**Important** Highly advisable to copy all these scripts out of the repository, and edit them so they point to your environment. Do not check in your local changes to these scripts.

### `countBatchesByTime.sh`
Creates a running count of all completed batches, by directory crawling the "Batch output" tree. **Expensive** Because this uses `find`, when there get to be 4000 or more batches, this script takes 4 minutes to run. Creates a lot of network traffic. If you must, you should change the sleep time in it from 120sec to 10 minutes. Batches grow slowly. Best used when run in the background and redirected to a file, which you can `tail` to see the results.

Start this when you run multiple. Outputs a running total of the completed batches, with time. Typical output:

|
15:43|6979
15:52|6979
15:58|6981

Which is the 24 hour time, and the number of batches.

### `countUnderwayBatches.sh`
Quick spot check to see how many jobs are underway. (Counts the `underway` folder files.). Not much different from `$(ls underway | wc)`

### `findBatchInWorksList.sh`
Outputs data you can use to gauge approximate completion status. Looks through running java processes to see which batches they are working on (approximately): output is the line in the worksList*n*.txt file. Since you set up the worksList files, you should have an idea of the completion fraction: these workLists contain 240 lines, so we see from this output that they're mostly complete:

bigRuns/worksList17.txt:**230**:W20325,14258110,
bigRuns/worksList21.txt:**209**:W23703,14259049,
bigRuns/worksList7.txt:**223**:W1KG11666,14255703,

### `topStats.sh`
A reduced set of the `top` command, to highlight the highest CPU usage tasks.

### `findNewerBatches.sh`
A not very useful, but expensive, command, which scans the batch output tree to count how many batch.xml files have been created in the last *n* minutes, where *n* is a positive integer. Output is `ls -l` format of all `batch.xml` files created in the last *n* minutes.

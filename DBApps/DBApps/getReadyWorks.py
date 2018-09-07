#!/usr/bin/env python3
import argparse
import csv
from typing import Union

import pymysql as mysql

from DBApps.DBApp import DBApp
from config.config import *
import pymysql
import pathlib
import os
import datetime
import DBApps.Writers.progressTimer
from DBApps.DBAppArgs import DBAppArgs, DbArgNamespace

def getRawReadyWorks(self, dbConfig, outputDir, maxRows):
    """

    :param dbConfig:
    :param outputDir:
    :param maxRows:
    :return:
    """
    dbConnection = self.start_connect(dbConfig)

# First, get the list of works for volumes which need uploading
with dbConnection:
    workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)
    workCursor.execute(f'select * from ReadyWorksNeedsBuilding limit {maxRows:d} ;')
    workVolumeResults: list = workCursor.fetchall()

    outfile: pathlib.Path = pathlib.Path(outputDir) \
                            / f'ReadyWorks{datetime.datetime.now().strftime("%y%m%e%H%M%S"):s}'

    with outfile.open("w", newline='') as fw:
        csvwr = csv.DictWriter(fw, fieldNames)
        csvwr.writeheader()
        for resultRow in workVolumeResults:
            downRow = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
            csvwr.writerow(downRow)


class GetReadyWorks(DBApp):
    """
    Fetch all ready works
    """
    def validateExpectedColumns(self, workCursor: mysql.cursors.Cursor) -> None:
        pass

    def __init__(self, options: DbArgNamespace) -> None:
        """
        :param: self
        :param: options
        :rtype: object
        """
        super().__init__()
        self._options = options
        self.ExpectedColumns = ['WorkName', 'HOLLIS', 'Volume', 'OutlineUrn', 'PrintMasterUrn']
        self.getReadyWorks()


def getReadyWorks(self):
    """
    Entry point for getting works
    :return:
    """
    grArgs = SetupParse()
    gr = GetReadyWorks(rrArgs)
    myrs = gr.GetResults()
    gr.PutResults(rrArgs.results, myrs)

    myArgs = GetReadyWorksArgs()
    parseByDBArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    # default create mode is 777
    if not os.path.exists(outRoot):
        os.mkdir(outRoot)

    # getResultsById(dbConfig, outRoot, myArgs.numWorks)
    # jimk: try to make a little more visible and less greedy
    getResultsByCount(dbConfig, outRoot, myArgs.numWorks)


def getResultsById(dbConfig, outputDir, maxRows: int):
    """
    Get WebAdminResults and write to directory.
    :param maxRows:
    :param dbConfig:
    :param outputDir:
    :return:
    """

    readyWorkCount = 0
    fetchedSets = 0
    readSets = 0

    dbConnection = start_connect(dbConfig)

    # First, get the list of works for volumes which need uploading
    with dbConnection:
        workCursor: pymysql.cursors = dbConnection.cursor()

        workCursor.execute(f'select distinct rwnd.workId from ReadyWorksNotDeposited rwnd \
                            join Volumes v on (rwnd.Volume = v.label) \
                            where not v.Queued order by workName asc limit {maxRows} ;')

        workIdResults: list = workCursor.fetchall()

        readyWorkCount = len(workIdResults)
        workCursor.close()
        workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)

        ticker = DBApps.Writers.progressTimer.ProgressTimer(maxRows, 10)

        # Build the output path
        outfile: pathlib.Path = pathlib.Path(outputDir) / datetime.datetime.now().strftime("%y%m%e%H%M%S")
        with outfile.open("w", newline='') as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            # one output file
            fieldNames = ['WorkName', 'HOLLIS', 'Volume', 'OutlineOSN', 'PrintMasterOSN']
            csvwr = csv.DictWriter(fw, fieldNames)

            for workTuple in workIdResults:
                workCursor.callproc('GetReadyVolumesByWorkId', workTuple)
                workVolumeResults: list = workCursor.fetchall()

                readSets += 1
                if len(workVolumeResults) <= 0:
                    continue
                # Only count results with fields back
                fetchedSets += 1
                assert isinstance(ticker, object)
                ticker.tick()

                csvwr.writeheader()
                for resultRow in workVolumeResults:
                    downRow = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                    csvwr.writerow(downRow)
                if fetchedSets == maxRows:
                    break
    print(f"Total retrieved work Ids: {readyWorkCount}. Read sets: {readSets}.  Fetched sets: {fetchedSets}")


def getResultsByCount(dbConfig, outputDir, maxWorks: int):
    """
    Get WebAdminResults and write to directory.
    :param maxWorks:
    :param dbConfig:
    :param outputDir:
    :return:
    """
    dbConnection = start_connect(dbConfig)
    # TODO: SSDictCursor? Each result set is small, but there are many of them
    workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)

    with dbConnection:
        # Build the output path
        outfile: pathlib.Path = pathlib.Path(outputDir) / datetime.datetime.now().strftime("%y%m%d%H%M%S")
        with outfile.open("w", newline='') as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            # one output file
            fieldNames = ['WorkName', 'HOLLIS', 'Volume', 'OutlineUrn', 'PrintMasterUrn']
            csvwr = csv.DictWriter(fw, fieldNames)
            print(f'Calling GetReadyVolumes for n = {maxWorks} ')
            workCursor.callproc('GetReadyVolumes', (maxWorks,))
            tt = DBApps.Writers.progressTimer.ProgressTimer(maxWorks, 5)

            # ReadyVolumes can return multiple sets
            hasNext: bool = True
            while hasNext:
                workVolumes = workCursor.fetchall()
                nVols = len(workVolumes)
                print(f"Received {nVols} volumes")
                tt.tick()
                if len(workVolumes) > 0:
                    csvwr.writeheader()
                    for resultRow in workVolumes:
                        down_row = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                        csvwr.writerow(down_row)
                hasNext = workCursor.nextset()


#
# ----------------        MAIN     --------------------




def getByCount():
    myArgs = GetReadyWorksArgs()
    parseByDBArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    if not os.path.exists(outRoot):
        # default create mode is 777
        os.mkdir(outRoot)

    getResultsByCount(dbConfig, outRoot, myArgs.numWorks)

# ----------------        Argument parsers     --------------------


def str2date(arg: str) -> datetime.datetime:
    """
    parses date given in yyyy-mm-dd
    """
    return datetime.datetime.strptime(arg, "%Y-%m-%d")


class GetReadyWorksParser(DBAppArgs):
    """
    Specifies arguments for get ready works
    """
    def __init__(self, description: str, usage: str):
        super().__init__(description, usage)
        self._parser.add_argument('-n', '--numWorks',
                                  help='how many works to fetch',
                                  default=10, type=int)
        self._parser.add_argument('results',
                                  help='Output path name. May overwrite existing contents',
                                  type=DBAppArgs.writableExpandoFile)


#-------------  end class definitions

def SetupParse() -> object:

    p = GetReadyWorksParser(
        description='Downloads ready works to folder, creating files related to folder',
        usage="%(prog)s | -d DBAppSection:DbAppFile [ -n default(200) ] resultPath")
    return p.parsedArgs


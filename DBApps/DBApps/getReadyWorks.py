#!/usr/bin/env python3
import argparse
import csv

from config.config import *
import pymysql
import pathlib
import os
import datetime


class getArgs:
    """
    Holds command line arguments
    """
    pass


def setup_config(drsDbConfig: str) -> DBConfig:
    """
    gets config values for setup
    :param drsDbConfig: in section:file format
    :return:
    """
    try:
        args: list = drsDbConfig.split(':')
        dbName = args[0]
        dbConfigFile = os.path.expanduser(args[1])
    except IndexError:
        raise IndexError('Invalid argument %s: Must be formatted as section:file ' % drsDbConfig)

    return DBConfig(dbName, dbConfigFile)


def getRawReadyWorks(dbConfig, outputDir, maxRows):
    """

    :param dbConfig:
    :param outputDir:
    :param maxRows:
    :return:
    """
    dbConnection = start_connect(dbConfig)

    # First, get the list of works for volumes which need uploading
    with dbConnection:
        workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)
        workCursor.execute(f'select * from ReadyWorksNeedsBuilding limit {maxRows:d} ;')
        workVolumeResults: list = workCursor.fetchall()

        outfile: pathlib.Path = pathlib.Path(outputDir) \
                                / f'ReadyWorks{datetime.datetime.now().strftime("%y%m%e%H%M%S"):s}'

        with outfile.open("w", newline='') as fw:
            fieldNames = ['WorkName', 'HOLLIS', 'Volume', 'OutlineOSN', 'PrintMasterOSN']
            csvwr = csv.DictWriter(fw, fieldNames)
            csvwr.writeheader()
            for resultRow in workVolumeResults:
                downRow = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                csvwr.writerow(downRow)

def getResultsByName(dbConfig, outputDir, maxRows):
    """

    :param dbConfig:
    :param outputDir:
    :param maxRows:
    :return:
    """
    dbConnection = start_connect(dbConfig)

    # First, get the list of works for volumes which need uploading
    with dbConnection:
        workCursor: pymysql.cursors = dbConnection.cursor()

        workCursor.execute(f'select distinct workId from Works where WorkName in (  \
                           \'W00EGS1017042\', \'W00EGS1017169\', \'W00KG03797\', \'W00KG09824\', \'W12171\', \'W12362\', \'W17209\', \'W19993\', \'W1KG2855\', \'W1KG3460\', \'W1KG4215\', \'W1KG4228\', \'W1KG4313\', \'W1KG4313\', \'W1KG5256\', \'W1KG5258\', \'W1KG5478\', \'W1KG5488\', \'W1KG5945\', \'W1KG6007\', \'W1KG6058\', \'W1KG6152\', \'W1KG6160\', \'W1KG6288\', \'W1KG8579\', \'W1KG8724\', \'W1KG8837\', \'W1KG8855\', \'W1KG8896\', \'W1KG8934\', \'W1KG9090\', \'W1KG9121\', \'W1KG9561\', \'W1KG9563\', \'W1PD105801\', \'W1PD105849\', \'W1PD105855\', \'W1PD105864\', \'W1PD105899\', \'W1CZ1293\', \'W1CZ2403\', \'W1CZ674\', \'W1KG11708\', \'W1KG14505\', \'W1KG15407\', \'W1KG1610\', \'W1KG1616\', \'W1KG16696\', \'W1KG2230\') \
                            ;')

        workIdResults: list = workCursor.fetchall()

        workCursor.close()
        workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)

        # Build the output path
        outfile: pathlib.Path = pathlib.Path(outputDir) / datetime.datetime.now().strftime("%y%m%e%H%M%S")
        with outfile.open("w", newline='') as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            # one output file
            fieldNames = ['WorkName', 'HOLLIS', 'Volume', 'OutlineOSN', 'PrintMasterOSN']
            csvwr = csv.DictWriter(fw, fieldNames)

            for workTuple in workIdResults:
                print(workTuple)
                workCursor.callproc('GetReadyVolumesByWorkId', workTuple)
                workVolumeResults: list = workCursor.fetchall()

                csvwr.writeheader()
                for resultRow in workVolumeResults:
                    downRow = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                    csvwr.writerow(downRow)


def getResultsById(dbConfig, outputDir, maxRows:int):
    """
    Get results and write to directory.
    :param maxRows:
    :param dbConfig:
    :param outputDir:
    :return:
    """
    dbConnection = start_connect(dbConfig)

    # First, get the list of works for volumes which need uploading
    with dbConnection:
        workCursor: pymysql.cursors = dbConnection.cursor()

        workCursor.execute(f'select distinct workId from ReadyWorksNeedsBuilding \
        order by workName asc limit {maxRows:d} ;')

        workIdResults: list = workCursor.fetchall()

        workCursor.close()
        workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)

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

                csvwr.writeheader()
                for resultRow in workVolumeResults:
                    downRow = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                    csvwr.writerow(downRow)

def getResultsByCount(dbConfig,outputDir, maxWorks: int):
    """
    Get results and write to directory.
    :param maxRows:
    :param dbConfig:
    :param outputDir:
    :return:
    """
    dbConnection = start_connect(dbConfig)
    workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)

    with dbConnection:
        # Build the output path
        outfile: pathlib.Path = pathlib.Path(outputDir) / datetime.datetime.now().strftime("%y%m%e%H%M%S")
        with outfile.open("w", newline='') as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            # one output file
            fieldNames = ['WorkName', 'HOLLIS', 'Volume', 'OutlineOSN', 'PrintMasterOSN']
            csvwr = csv.DictWriter(fw, fieldNames)
            workCursor.callproc('GetReadyVolumes', (maxWorks,))

            # TestReadyVolumes can return multiple sets
            hasNext: bool = True
            while hasNext:
                workVolumes = workCursor.fetchall()
                if len(workVolumes) > 0:
                    csvwr.writeheader()
                    for resultRow in workVolumes:
                        down_row = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                        csvwr.writerow(down_row)
                hasNext = workCursor.nextset()

def start_connect(cfg):
    """
    Opens a database connection using the DBConfig
    :param cfg:
    :return:
    """
    return pymysql.connect(read_default_file=cfg.db_cnf,
                           read_default_group=cfg.db_host,
                           charset='utf8')


#
# ----------------        MAIN     --------------------
def getReadyWorks():
    myArgs = getArgs()
    parseByDBArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    # default create mode is 777
    if not os.path.exists(outRoot):
        os.mkdir(outRoot)

    getResultsById(dbConfig, outRoot, myArgs.numWorks)

def getNamedWorks():
    myArgs = getArgs()
    parseByNameArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    # default create mode is 777
    if not os.path.exists(outRoot):
        os.mkdir(outRoot)

    getResultsByName(dbConfig, outRoot, myArgs.numWorks)


def getByCount():
    myArgs = getArgs()
    parseByDBArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    if not os.path.exists(outRoot):
    # default create mode is 777
        os.mkdir(outRoot)

    getResultsByCount(dbConfig, outRoot, myArgs.numWorks)

def updateBuildStatus():
    """
    Updates the build status of a work with its date and build directory
    :return:
    """
    myArgs = getArgs()
    parseByUpdateArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    dbConnection = start_connect(dbConfig)
    uCursor = dbConnection.cursor()
    hadBarf=False
    errVolPersist=""

    try:
        for volDir in volumesForBatch(myArgs.buildPath):
            errVolPersist=volDir
            uCursor.callproc('UpdateBatchBuild', (volDir, myArgs.buildPath, myArgs.buildDate, myArgs.result))
    except:
        import sys
        exc = sys.exc_info()
        print("unexpected error for volume, ", errVolPersist, exc[0], exc[1], file = sys.stderr)
        dbConnection.rollback()
        hadBarf = True
    finally:
        uCursor.close()
        if not hadBarf:
            dbConnection.commit()
        dbConnection.close()


def volumesForBatch( batchFolder : str) -> str:
    """
    Returns a JSON array of the folders in a batch build project.
    These folders are one per volume, named for the volume,
    so this returns a list of volumes in a specific batch.
    :param batchFolder:
    :return:
    """
    for root, dirs, folders in os.walk(batchFolder):
        return dirs

# ----------------        Argument parsers     --------------------

def mustExistDirectory(path : str):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError
    for root, dirs, files in os.walk(path, True):
        if len(dirs) == 0:
            raise argparse.ArgumentTypeError
        else:
            return path

def parseByUpdateArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Updates the build status of a work with its build path and build date '
                                                  'name', usage="%(prog)s | -d DBAppSection:DbAppFile "
                                                                "workName buildPath buildDate"
                                      )
    _parser.add_argument('-d', '--drsDbConfig',
                         help='specify section:configFileName',required=True)
    _parser.add_argument("buildPath", help='Folder containing batch.xml and objects', type=mustExistDirectory)
    _parser.add_argument("result", help='String representing the result')
    _parser.add_argument("buildDate", nargs='?', help='build date. Defaults to time this call was made.',
                         default=datetime.datetime.now(), type=datetime.datetime)

    _parser.parse_args(namespace=argNamespace)

def parseByDBArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(
        description='Downloads ready works to folder, creating files related to folder '
                    'name', usage="%(prog)s | -d DBAppSection:DbAppFile "
                                  "[ -n n How many works to download. ] resultsRoot"
        )
    _parser.add_argument('-d', '--drsDbConfig',
                         help='specify section:configFileName', required=True)
    _parser.add_argument('-n', '--numWorks', help='how many works to fetch', default=10, type=int)
    _parser.add_argument("resultsRoot", help='Directory containing results. Overwrites existing contents')

    _parser.parse_args(namespace=argNamespace)

def parseByNameArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Downloads ready works to folder, creating files related to folder '
                                                  'name', usage="%(prog)s | -d DBAppSection:DbAppFile "
                                                                "[ -n n How many works to download. ] resultsRoot"
                                      )
    _parser.add_argument('-d', '--drsDbConfig',
                         help='specify section:configFileName')
    _parser.add_argument('-n', '--numWorks', help='how many works to fetch', default=10, type=int)
    _parser.add_argument("resultsRoot", help='Directory containing results. Overwrites existing contents')

    _parser.parse_args(namespace=argNamespace)


if __name__ == '__main__':
    updateBuildStatus()

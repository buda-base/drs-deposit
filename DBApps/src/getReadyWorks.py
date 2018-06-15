import argparse
import csv
from DBApp.config import *
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


def getResults(dbConfig, outputDir, maxRows):
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


def getResultsTake1(dbConfig, outputDir, maxRows):
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

        workCursor.execute(
            "select distinct workId from ReadyWorksNeedsBuilding order by workName asc limit %d ;" % (maxRows,))
        # if we use dbConnection.cursor(pymysql.cursors.DictCursor) expect[ {'workId' : nnnn },....]
        # expected [ (workId,),....]
        workIdResults: list = workCursor.fetchall()
        # when we open a dict cursor, use this syntax
        # [workIdList.append(item['workId']) for item in workIdResults]
        #
        workCursor.close()
        workCursor = dbConnection.cursor(pymysql.cursors.DictCursor)
        for workTuple in workIdResults:
            workCursor.callproc('GetReadyVolumesByWorkId', workTuple)
            workVolumeResults: list = workCursor.fetchall()

            # All the rows should have the same WorkName
            # @TODO: rethink serializing by time?
            # fileName = "%s_%s" % (workVolumeResults[0]['WorkName'],  datetime.datetime.now().strftime("%y%m%e%H%M%S"))
            outfile: pathlib.Path = pathlib.Path(outputDir) / workVolumeResults[0]['WorkName']

            with outfile.open("w", newline='') as fw:
                fieldNames = ['WorkName', 'HOLLIS', 'Volume', 'OutlineOSN', 'PrintMasterOSN']
                csvwr = csv.DictWriter(fw, fieldNames)
                csvwr.writeheader()
                for resultRow in workVolumeResults:
                    downRow = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                    csvwr.writerow(downRow)


def getResultsTake2(dbConfig, outputDir, maxRows):
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
def main():
    myArgs = getArgs()
    parseArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    # default create mode is 777
    if not os.path.exists(outRoot):
        os.mkdir(outRoot)

    getResultsTake2(dbConfig, outRoot, myArgs.numWorks)


# ----------------        MAIN     --------------------
def parseArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Downloads ready works to folder, creating files related to folder '
                                                  'name', usage="%(prog)s | -d DBAppSection:DbAppFile "
                                                                "[ -n n How many works to download. ] resultsRoot"
                                      )
    _parser.add_argument('-d', '--drsDbConfig',
                         help='specify section:configFileName')
    _parser.add_argument('-n', '--numWorks', help='how many works to fetch', default=10)
    _parser.add_argument("resultsRoot", help='Directory containing results. Overwrites existing contents')

    _parser.parse_args(namespace=argNamespace)


if __name__ == '__main__':
    main()

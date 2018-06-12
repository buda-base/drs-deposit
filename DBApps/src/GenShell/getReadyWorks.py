import argparse
import sys
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


def setup_config(drsDbConfig:object) -> DBConfig:
    """
    gets config values for setup
    :param drsDBConfig: in section:file format
    :return:
    """
    try:
        args: object = drsDbConfig.split(':')
        dbName = args[0]
        dbConfigFile = os.path.expanduser(args[1])
    except IndexError:
        raise IndexError('Invalid argument %s: Must be formatted as section:file ' % drsDbConfig)

    return DBConfig(dbName, dbConfigFile)


def getResults(dbConfig, outputDir, maxRows):
    """
    Get results and write to directory.
    :param dbConfig:
    :param outputDir:
    :return:
    """
    dbConnection = start_connect(dbConfig)

    # First, get the list of works for volumes which need uploading
    with dbConnection:
        workCursor : pymysql.cursors = dbConnection.cursor()
        workIds : object

        workCursor.execute("select distinct workId from ReadyWorksNeedsBuilding limit %d ;" % (maxRows,))
        # if we use dbConnection.cursor(pymysql.cursors.DictCursor) expect[ {'workId' : nnnn },....]
        # expected [ (workId,),....]
        workIdResults: list = workCursor.fetchall()
        #when we open a dict cursor, use this syntax
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

            # wr.writelines jams them all on same lines
            with outfile.open("w") as fw:
                fw.write('\n'.join([item['Volume'] for item in workVolumeResults]))
                # Unglaubische dumm
                fw.write('\n')


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
def main(args):

    myArgs = getArgs()
    parseArgs(myArgs)
    dbConfig = setup_config(myArgs.drsDbConfig)
    #
    outRoot: str = os.path.expanduser(myArgs.resultsRoot)

    # defult create mode is 777
    if not os.path.exists(outRoot):
        os.mkdir(outRoot)

    getResults(dbConfig, outRoot, myArgs.numWorks)


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
    main(sys.argv[1:])
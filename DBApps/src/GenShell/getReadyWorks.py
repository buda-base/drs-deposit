import argparse
import sys
from DBApp import config
import pymysql
import pathlib
import os
import datetime


class getArgs:
    """
    Holds command line arguments
    """
    pass


def setupConfig(drsDBConfig):
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
        raise IndexError('Invalid argument %s: Must be formatted as section:file ' % drsDBConfig)

    return  config.DBConfig(dbName, dbConfigFile)

def getResults(dbConfig, outputDir):
    """
    Get results and write to directory.
    :param dbConfig:
    :param outputDir:
    :return:
    """
    dbConnection = start_connect(dbConfig)

    # First, get the list of works for volumes which need uploading
    with dbConnection:
        work_cursor : pymysql.cursors = dbConnection.cursor()
        workIds : object

        work_cursor.execute("select distinct workId from ReadyWorksNeedsBuilding;")
        # expected [ {'workId' : nnnn },....]
        workIdResults: list  = work_cursor.fetchall()
        workIdList: list
        [workIdList.append(item['workId']) for item in workIdResults]
        for workId in workIdList:
            work_cursor.callproc('GetReadyVolumesByWorkId')
            work_volume_results : list = work_cursor.fetchall()

            # All the rows should have the same WorkName
            outFile : pathlib.Path = outputDir / "%s_%s" % work_volume_results[0]['WorkName'], datetime.datetime.now().strftime("%y%m%e%H%M%S")

            # wr.writelines jams them all on same lines
            with outFile.open("w") as fw:
                fw.write('\n'.join([item['Volume'] for item in work_volume_results]))





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
    dbConfig = setupConfig(myArgs.drsDbConfig)
    #
    outRoot : object = pathlib.Path(myArgs.resultsRoot)

    # defult create mode is 777
    if not os.exists(outRoot):
        os.mkdir(outRoot)

    getResults(dbConfig, outRoot)


# ----------------        MAIN     --------------------
def parseArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Downloads ready works to folder, creating files related to folder name', usage='%(prog)s | -d DBAppSection:DbAppFile outputs to db whose parameters are given in config file')

    _parser.add_argument('-d', '--drsDbConfig',
                         help='specify section:configFileName')
    _parser.add_argument("resultsRoot", help='Directory containing results. Overwrites existing contents')

    _parser.parse_args(namespace=argNamespace)



if __name__ == '__main__':
    main(sys.argv[1:])
import argparse
import os
from typing import Union, Tuple

from DBApps.DBApp import DBApp


class GetUpdateArgs(DBApp):
    """
    Namespace for arg parser
    """
    pass


# noinspection PyBroadException
def updateBuildStatus():
    """
    Updates the build status of a work with its date and build directory
    :return:
    """
    myArgs = GetUpdateArgs()
    parseByUpdateArgs(myArgs)
    updateBuildStatusCore(myArgs.drsDbConfig, myArgs.buildPath, myArgs.buildDate, myArgs.result)


def get_tree_values(path: str) -> Tuple[Union[int, Any], Union[int, Any]]:
    """Return total size of files in given path and subdirs."""

    total: int = 0
    fileCount: int = 0
    subTotal: int = 0
    subCount: int = 0

    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            subCount, subTotal = get_tree_values(entry.path)
        else:
            subTotal = entry.stat(follow_symlinks=False).st_size
            subCount = 1
        total += subTotal
        fileCount += subCount
    return fileCount, total

def updateBuildStatusCore(config, buildPath, buildDate, result):
    dbConfig = setup_config(config)
    dbConnection = start_connect(dbConfig)
    uCursor = dbConnection.cursor()
    hadBarf = False
    errVolPersist = ""
    try:
        for volDir in volumesForBatch(buildPath):
            buildPath = str(Path(buildPath).resolve())
            volPath = Path(buildPath, volDir)
            volFiles, volSize = get_tree_values(volPath)
            errVolPersist = volDir
            uCursor.execute(f'insert ignore BuildPaths ( `BuildPath`) values ("{buildPath}") ;')
            dbConnection.commit()
            uCursor.callproc('UpdateBatchBuild', (volDir, buildPath, buildDate, result, volFiles, volSize))

    except:
        import sys
        exc = sys.exc_info()
        print("unexpected error for volume, ", errVolPersist, exc[0], exc[1], file=sys.stderr)
        dbConnection.rollback()
        hadBarf = True
    finally:
        uCursor.close()
        if not hadBarf:
            dbConnection.commit()
        dbConnection.close()


def mustExistDirectory(path: str):
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
    _parser = argparse.ArgumentParser(
        description='Updates the build status of a work with its build path and build date '
                    'name', usage="%(prog)s | -d DBAppSection:DbAppFile "
                                  "buildPath result [buildDate]"
        )
    _parser.add_argument('-d', '--drsDbConfig',
                         help='specify section:configFileName', required=True)
    _parser.add_argument("buildPath", help='Folder containing batch.xml and objects', type=mustExistDirectory)
    _parser.add_argument("result", help='String representing the result')
    _parser.add_argument("buildDate", nargs='?', help='build date. Defaults to time this call was made.',
                         default=datetime.datetime.now(), type=str2date)

    _parser.parse_args(namespace=argNamespace)

def updateBuildStatusWrapper(configPath: str, buildPath: str, buildDate: datetime, result: str):
    """
    Mocks command line arguments
    :return:
    """
    updateBuildStatusCore(configPath, buildPath, buildDate, result)



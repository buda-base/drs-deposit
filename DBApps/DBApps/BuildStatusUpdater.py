"""
Update Build Status class
"""

# sys
import sys
import datetime
import os
# usr
from pathlib import Path
from typing import Tuple, Any, Union

from DBApps.DbAppParser import DbArgNamespace, str2date, DbAppParser, mustExistDirectory
from DBApps.DbApp import DbApp


class UpdateBuildParser(DbAppParser):
    """
    Parser for the Get Ready Related class
    Returns a structure containing fields:
    .drsDbConfig: str (from base class DBAppArgs
    .outline: bool
    .printmaster: bool
    .numResults: int
    .results: str (which will have to resolve to a pathlib.Path
    """

    def __init__(self, description: str, usage: str):
        """
        Constructor. Sets up the arguments
        """
        super().__init__(description, usage)
        self._parser.add_argument("buildPath", help='Folder containing batch.xml and objects', type=mustExistDirectory)
        self._parser.add_argument("result", help='String representing the result')
        self._parser.add_argument("buildDate", nargs='?', help='build date. Defaults to time this call was made.',
                                  default=datetime.datetime.now(), type=str2date)


def volumesForBatch(batchFolder: str) -> list:
    """
    The folders in a batch build project represent the BDRC Volumes in the
    batch build.
    :param batchFolder:
    :return: list of the folders in a batch build project
    """
    for root, dirs, folders in os.walk(batchFolder):
        return dirs


# noinspection PyBroadException
class BuildStatusUpdater(DbApp):
    """
    Sets up build status updating
    """

    def __init__(self, options: DbArgNamespace) -> None:
        """
        :param: self
        :param: options
        :rtype: object
        """
        # drsDbConfig is required
        try:
            super().__init__(options.drsDbConfig)
        except AttributeError:
            print("argument parsing error: drsDbConfig not found in args")
            sys.exit(1)

        self._options = options

    # noinspection PyBroadException
    def DoUpdate(self) -> None:
        """
        Update each volume in the options' buildPath
        """
        self.start_connect()
        conn = self.connection

        uCursor = conn.cursor()
        hadBarf = False
        errVolPersist = ""
        try:
            buildPath = self._options.buildPath
            for volDir in volumesForBatch(buildPath):
                fullBuildPath = str(Path(buildPath).resolve())
                volPath: Path = Path(fullBuildPath, volDir)

                volFiles, volSize = self.get_tree_values(str(volPath))
                errVolPersist = volDir

                uCursor.execute(f'insert ignore BuildPaths ( `BuildPath`) values ("{buildPath}") ;')
                conn.commit()

                uCursor.callproc('UpdateBatchBuild', (
                    volDir, buildPath, self._options.buildDate, self._options.result, volFiles, volSize))

        except:
            import sys
            exc = sys.exc_info()
            print("unexpected error for volume, ", errVolPersist, exc[0], exc[1], file=sys.stderr)
            conn.rollback()
            hadBarf = True
        finally:
            uCursor.close()
            if not hadBarf:
                conn.commit()
            conn.close()

    def get_tree_values(self, path: str) -> Tuple[Union[int, Any], Union[int, Any]]:
        """
        Get file counts on directory and subdirectories.
        :param path: path containing files and folders to be counted
        :returns: total size of files and file count
        :rtype: tuple(int int)
        """

        total: int = 0
        fileCount: int = 0

        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                subCount, subTotal = self.get_tree_values(entry.path)
            else:
                subTotal = entry.stat(follow_symlinks=False).st_size
                subCount = 1
            total += subTotal
            fileCount += subCount
        return fileCount, total

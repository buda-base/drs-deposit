"""
DbApp class to update Build Status

"""
import sys
import os
from datetime import datetime
import argparse

from DBApps.DbApp import DbApp
from DBApps.DbAppParser import DbAppParser, DbArgNamespace, writableExpandoFile


def mustExistDirectory(path: str):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError
    for root, dirs, files in os.walk(path, True):
        if len(dirs) == 0:
            raise argparse.ArgumentTypeError
        else:
            return path

class updateBuildStatusParser(DbAppParser):
    """
    Specifies arguments for get ready works
    """

    def __init__(self, description: str, usage: str):
        super().__init__(description, usage)

        self._parser.add_argument("buildPath", help='Folder containing batch.xml and objects', type=mustExistDirectory)
        self._parser.add_argument("result", help='String representing the result')
        self._parser.add_argument("buildDate", nargs='?', help='build date. Defaults to time this call was made.',
                             default=datetime.datetime.now(), type=str2date)


class GetReadyWorks(DbApp):
    """
    Fetch all ready works
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
        self.ExpectedColumns = ['WorkName', 'HOLLIS', 'Volume', 'OutlineUrn', 'PrintMasterUrn']

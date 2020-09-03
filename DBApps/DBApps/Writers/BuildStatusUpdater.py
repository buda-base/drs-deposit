"""
DbApp class to update Build Status

"""
import sys
from datetime import datetime

from DBApps.DbApp import DbApp
from DBAppParser import DbAppParser, DbArgNamespace, mustExistDirectory, str2date


class UpdateBuildStatusParser(DbAppParser):
    """
    Specifies arguments for get ready works
    """

    def __init__(self, description: str, usage: str):
        super().__init__(description, usage)

        self._parser.add_argument("buildPath", help='Folder containing batch.xml and objects', type=mustExistDirectory)
        self._parser.add_argument("result", help='String representing the result')
        self._parser.add_argument("buildDate", nargs='?', help='build date. Defaults to time this call was made.',
                                  default=datetime.now(), type=str2date)


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

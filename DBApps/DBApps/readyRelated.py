"""
Get Ready Related works class
"""

# sys
import sys
from abc import ABC
# usr
from DBApps.DbAppParser import DbAppParser, DbArgNamespace, writableExpandoFile
from DBApps.DbApp import DbApp


class ReadyRelatedParser(DbAppParser):
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
        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-o', '--outline', action='store_true', help="Chooses works with outlines")
        group.add_argument('-p', '--printmaster', action='store_true', help="Chooses works with print masters")
        self._parser.add_argument('-n', '--numResults', help="maximum number to download",
                                  default=10, type=int)

        self._parser.add_argument("results",
                                  help='Output path name. May overwrite existing contents',
                                  type=writableExpandoFile)


class ReadyRelated(DbApp, ABC):
    """
    Gets related works
    """
    _options: DbArgNamespace

    @property
    def TypeString(self) -> str:
        """
        Map the option to a string. Calculated, readonly property
        Case sensitive, since this is used to build a call to a SPROC in a mySQL
        database, which has a mixed case namespace
        :return:
        """
        rs = None

        if self._options.outline:
            rs = "Outlines"
        if self._options.printmaster:
            rs = "PrintMasters"
        return rs

    def __init__(self, options: DbArgNamespace) -> None:
        """
        :param: self
        :param: DbArguments
        :rtype: object
        """
        # drsDbConfig is required
        try:
            super().__init__(options.drsDbConfig)
        except AttributeError:
            print("argument parsing error: drsDbConfig not found in args")
            sys.exit(1)

        self._options = options
        self.ExpectedColumns = ['WorkName', 'HOLLIS', 'Volume']

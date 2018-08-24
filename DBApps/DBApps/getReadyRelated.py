"""
Get Ready Related works class
"""
from DBApps.DBArgs import DBAppArgs, Args
from DBApps.DBApp import DBApp
from pymysql import *


class GetReadyRelatedParser(DBAppArgs):
    """
    Parser for the Get Ready Related class
    """

    def __init__(self, description: str, usage: str):
        """
        Constructor. Sets up the arguments
        """
        super().__init__(description, usage)
        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-o', '--outline', action='store_true', help="Chooses works with outlines")
        group.add_argument('-p', '--printMaster', action='store_true', help="Chooses works with print masters")
        self._parser.add_argument("resultsRoot", help='Output directory. May overwrite existing contents')


class GetReadyRelated(DBApp):
    """
    Gets related works
    """

    _options: Args
    _dbConnection: Connection

    def SetupParse(self):
        """
        Sets up and parses argument
        :return:
        """
        p = GetReadyRelatedParser(description="Fetch Works information which have outlines or print masters",
                                  usage=" -o --outline | -p --printmaster resultsRoot")
        self._options = p.parsedArgs

    def __init__(self):
        self.SetupParse()
        self.config = self._options.drsDBconfig
        start_connect(self.config)

import csv
import sys
from DBApps.DbAppParser import DbAppParser, DbArgNamespace, mustExistFile
from DBApps.DbApp import DbApp
from DBApps.Writers.progressTimer import ProgressTimer


class AddRelatedParser(DbAppParser):
    """
     Parser for the RelatedAdder class
     Returns a structure containing fields:
     .drsDbConfig: str (from base class DBAppArgs)
     .outline: bool
     .printmaster: bool

     .sourceFile: str (which will have to resolve to a pathlib.Path
     """

    def __init__(self, description: str, usage: str):
        """
        Constructor. Sets up the arguments
        """
        super().__init__(description, usage)
        group = self._parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-o', '--outline', action='store_true', help="Add works with outlines")
        group.add_argument('-p', '--printmaster', action='store_true', help="Add works with print masters")

        self._parser.add_argument("sourceFile",
                                  help='Source file',
                                  type=mustExistFile)


class RelatedAdder(DbApp):
    """
    Adds a list of workNames to the repository of outlines or printmasters.
    """
    _options: DbArgNamespace

    def __init__(self, options):
        """
        :type options: DbArgNamespace
        """
        try:
            super().__init__(options.drsDbConfig)
        except AttributeError:
            print("argument parsing error: drsDbConfig not found in args")
            sys.exit(1)

        self._options = options

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
            rs = "Outline"
        if self._options.printmaster:
            rs = "PrintMaster"
        return rs

    @property
    def LabelString(self) -> str:
        """
        Map the option to a string.
        :return:
        """
        rs = None

        if self._options.outline:
            rs = "-Outline"
        if self._options.printmaster:
            rs = "-PrintMaster"
        return rs

    def Add(self, sproc: str, sourceFile: str) -> None:
        """
        Adds the list of workNames to the related type specified in the args
        Suffixes the work name with the LabelString
        :param sproc: routine to call
        :param sourceFile: file to read with arguments
        :return:
        """
        self.start_connect()
        ls = self.LabelString

        num_lines = sum(1 for line in open(sourceFile))
        tt = ProgressTimer(num_lines, 10)

        with self.connection.cursor() as workCursor:
            with open(sourceFile, newline='') as src:
                hasHeader = csv.Sniffer().has_header(src.read(512))
                src.seek(0)
                srcCsv = csv.reader(src, delimiter=',', quotechar='"')
                for row in srcCsv:
                    if hasHeader:
                        hasHeader = False
                        continue
                    # the sproc takes a label argument
                    # This is generated from the first column, or the second col
                    # if it is there
                    if len(row) > 1:
                        label = row[1]
                    else:
                        label = f'{row[0]}{ls}'
                    workCursor.callproc(sproc, (row[0], label,))
                    tt.tick()
            self.connection.commit()


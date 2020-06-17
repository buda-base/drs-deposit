"""
Created 2018-VIII-24
@author: jimk
"""

import pymysql as mysql
from config.config import DBConfig
import os


class DbApp:
    """
    Base class for database applications
    """
    _dbConfig: DBConfig
    _cn: mysql.Connection
    _dbConnection: mysql.Connection
    _expectedColumns: list = None

    def __init__(self, dbConfig: DBConfig):
        self.dbConfig = dbConfig
        self.connection = None
        self.ExpectedColumns = []

    def start_connect(self) -> None:
        """
        Opens a database connection using the DBConfig
        :return: Nothing. Sets class connection property
        """
        self.connection = mysql.connect(read_default_file=self.dbConfig.db_cnf,
                                        read_default_group=self.dbConfig.db_host,
                                        charset='utf8')

    @property
    def ExpectedColumns(self) -> list:
        """
        If a subclass returns a result set from a query, you may only want some of the query columns
        If this list is empty, all the data set columns are returned
        :return:
        """
        return self._expectedColumns

    @ExpectedColumns.setter
    def ExpectedColumns(self, value: list):
        assert isinstance(value, list)
        self._expectedColumns = value

    @property
    def dbConfig(self) -> DBConfig:
        return self._dbConfig

    @dbConfig.setter
    def dbConfig(self, drsDbConfig: str):
        """
        gets dbConfig values for setup
        :param drsDbConfig: in section:file format
        :return:
        """
        if drsDbConfig is None:
            self._dbConfig = None
            return

        try:
            args: list = drsDbConfig.split(':')
            dbName = args[0]
            dbConfigFile = os.path.expanduser(args[1])
        except IndexError:
            raise IndexError('Invalid argument %s: Must be formatted as section:file ' % drsDbConfig)

        self._dbConfig = DBConfig(dbName, dbConfigFile)

    @property
    def connection(self) -> mysql.Connection:
        return self._cn

    @connection.setter
    def connection(self, value):
        self._cn = value

    def validateExpectedColumns(self, cursorDescription: list) -> None:
        """
        Validates the cursor after a call to the database. Checks for
        the required columns (from member ExpectedColumns) in the output

        :param cursorDescription: tuple of tuples
        :return: Throws ValueError on fail
        """
        found = False
        for expectedColumn in self.ExpectedColumns:
            found = False
            for cursorTuple in cursorDescription:
                if cursorTuple[0] == expectedColumn:
                    found = True
                    break
            # each expected column must be in the list
            if not found:
                break
        if not found:
            raise ValueError(f'SPROC did not return expected columns')

        # desc = queryCursor.description
        # hope something's here

    def GetSprocResults(self, sproc: str, maxWorks: int = 200) -> list:
        """
        call a sproc using the internal connection,
        validate the result columns with the internal member.

        :rtype: list of dictionary objects of results. Caller decodes format
        :param sproc: routine to call
        :param maxWorks: limit of return rows
        :returns: a list of dictionary items, each item is a return row
        """
        self.start_connect()

        rl: list[dict] = []

        hasNext: bool = True
        with self.connection:
            try:
                # jimk #drs-deposit 76. Dont use unbuffered cursor, which blocks access to the db
                # until it's done or cleared. (e.g. pyCharm queries
                workCursor: mysql.Connection.Cursor = self.connection.cursor(mysql.cursors.DictCursor)
                print(f'Calling {sproc} for n = {maxWorks} ')
                workCursor.callproc(f'{sproc}', (maxWorks,))
                self.validateExpectedColumns(workCursor.description)

                while hasNext:
                    resultRows = workCursor.fetchall()
                    rl.append(resultRows)
                    hasNext = workCursor.nextset()
            finally:
                # have to drain result sets if there was an exception (if
                while hasNext:
                    workCursor.fetchall()
                    hasNext = workCursor.nextset()
        return rl

    def CallAnySproc(self, sproc: str, *args):
        """
        Calls a routine without analyzing the result
        :param sproc: routine name
        :param args: arguments
        :return: true if there are any results, throws exception otherwise.
        Caller handles
        """
        self.start_connect()

        rl: list[dict] = []

        with self.connection:
            workCursor: mysql.Connection.Cursor = self.connection.cursor()
            print(f'Calling {sproc} for n = {maxWorks}')
            workCursor.callproc(f'{sproc}', tuple(arg for arg in args))
            workCursor.fetchall()  # wgaf

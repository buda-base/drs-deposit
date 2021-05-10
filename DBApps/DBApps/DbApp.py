"""
Created 2018-VIII-24
@author: jimk
"""
import logging
import sys

import pymysql
import pymysql as mysql

from DBApps.SprocColumnError import SprocColumnError
from config.config import DBConfig
import os


class DbApp:
    """
    Base class for database applications
    """
    _invoked_object: str
    _dbConfig: DBConfig
    _cn: mysql.Connection
    _dbConnection: mysql.Connection
    _expectedColumns: list = None
    _log: logging

    def __init__(self, db_config: str):
        self.dbConfig = db_config
        self.connection = None
        self.ExpectedColumns = []
        self._log = logging.getLogger(__name__)

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
    def dbConfig(self, drs_db_config: str):
        """
        gets dbConfig values for setup
        :param drs_db_config: in section:file format
        :return:
        """
        if drs_db_config is None:
            # noinspection PyTypeChecker
            self._dbConfig = None
            return

        try:
            args: list = drs_db_config.split(':')
            db_name = args[0]
            db_config_file = os.path.expanduser(args[1])
        except IndexError:
            raise IndexError('Invalid argument %s: Must be formatted as section:file ' % drs_db_config)

        self._dbConfig = DBConfig(db_name, db_config_file)

    @property
    def connection(self) -> mysql.Connection:
        return self._cn

    @connection.setter
    def connection(self, value):
        self._cn = value

    def validateExpectedColumns(self, cursor_description: list) -> None:
        """
        Validates the cursor after a call to the database. Checks for
        the required columns (from member ExpectedColumns) in the output

        :param cursor_description: tuple of tuples
        :return: Throws ValueError on fail
        """
        found = False
        found_columns: list = []

        # Data expected but not returned
        if cursor_description is None and len(self.ExpectedColumns) > 0:
            raise SprocColumnError(f'Invoked object {self._invoked_object} returned no expected data.')

        for expected_column in self.ExpectedColumns:
            found = False
            for cursor_tuple in cursor_description:
                if cursor_tuple[0] == expected_column:
                    found = True
                    found_columns.append(cursor_tuple[0])
                    break
            # each expected column must be in the list
            if not found:
                break
        if not found:
            raise SprocColumnError(
                f'Invoked object {self._invoked_object} Expected to return columns {self.ExpectedColumns}. Only '
                f'returned {found_columns}.')

        # desc = queryCursor.description
        # hope something's here

    def GetSprocResults(self, sproc: str, max_works: int = 200) -> list:
        """
        call a sproc using the internal connection,
        validate the result columns with the internal member.

        :rtype: list of dictionary objects of results. Caller decodes format
        :param sproc: routine to call
        :param max_works: limit of return rows
        :returns: a list of dictionary items, each item is a return row
        """

        self._invoked_object = sproc
        self.start_connect()

        rl: list[dict] = []

        has_next: bool = True
        with self.connection:
            try:
                # jimk #drs-deposit 76. Dont use unbuffered cursor, which blocks access to the db
                # until it's done or cleared. (e.g. pyCharm queries
                work_cursor: mysql.Connection.Cursor = self.connection.cursor(mysql.cursors.DictCursor)
                print(f'Calling {sproc} for n = {max_works} ')
                work_cursor.callproc(f'{sproc}', (max_works,))
                self.validateExpectedColumns(work_cursor.description)

                while has_next:
                    result_rows = work_cursor.fetchall()
                    rl.append(result_rows)
                    has_next = work_cursor.nextset()
            finally:
                # have to drain result sets if there was an exception (if
                while has_next:
                    work_cursor.fetchall()
                    has_next = work_cursor.nextset()
        return rl

    def CallAnySproc(self, sproc: str, *args) -> []:
        """
        Calls a routine without analyzing the result
        :param sproc: routine name
        :param out_arg_index:  If  there is an out arg, its index in the tuple of args
        :param args: arguments
        :return: true if there are any results, throws exception otherwise.
        Caller handles
        """
        self.start_connect()

        rl: [] = []

        with self.connection:

            work_cursor: mysql.Connection.Cursor = self.connection.cursor(mysql.cursors.DictCursor)

            sql_args = tuple(arg for arg in args)
            self._log.debug(f"Calling {sproc} args {':'.join(str(sql_arg) for sql_arg in sql_args)}")
            try:
                work_cursor.callproc(f'{sproc}', sql_args)
                has_next: bool = True
                while has_next:
                    result_rows = work_cursor.fetchall()
                    rl.append(result_rows)
                    has_next = work_cursor.nextset()
                self.connection.commit()
            except pymysql.Error as e:
                self._log.error("Error calling", exc_info=sys.exc_info())
                self.connection.rollback()
                raise e
        return rl

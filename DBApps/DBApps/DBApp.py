"""
Created 2018-VIII-24
@author: jimk
"""
from config.config import *
import pymysql as mysql
from abc import ABCMeta, abstractmethod


class DBApp(metaclass=ABCMeta):
    """
    Base class for database applications
    """
    _dbConfig: DBConfig
    _cn: mysql.Connection

    def __init__(self):
        self.dbConfig = None
        self.connection = None
        self.ExpectedColumns = []

    def start_connect(self, cfg: DBConfig):
        """
        Opens a database connection using the DBConfig
        :param cfg:
        :return:
        """
        self.connection = mysql.connect(read_default_file=cfg.db_cnf,
                                        read_default_group=cfg.db_host,
                                        charset='utf8')

    _expectedColumns: list = None

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

    @abstractmethod
    def validateExpectedColumns(self, workCursor: mysql.cursors.Cursor) -> None:
        """
        :summary: Abstract method to validate the db query output against the class' requirements
        returns or throws
        """
        pass

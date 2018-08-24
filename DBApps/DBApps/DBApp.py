"""
Created 2018-VIII-24
@author: jimk
"""
from config.config import *
import pymysql as mysql


class DBApp:
    """
    Base class for database applications
    """
    _dbConfig: DBConfig
    _cn: mysql.Connection

    def __init__(self):
        self.config = None
        self.connection = None

    def start_connect(self, cfg: DBConfig):
        """
        Opens a database connection using the DBConfig
        :param cfg:
        :return:
        """
        self.connection = mysql.connect(read_default_file=cfg.db_cnf,
                                        read_default_group=cfg.db_host,
                                        charset='utf8')

    @property
    def config(self) -> DBConfig:
        return self._dbConfig

    @config.setter
    def config(self, drsDbConfig: str):
        """
        gets config values for setup
        :param drsDbConfig: in section:file format
        :return:
        """
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

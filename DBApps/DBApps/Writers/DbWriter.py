"""
Created on Mar 6, 2018

@author: jsk
"""
# base class
import sys

from DBApps.Writers.listwriter import ListWriter

# Configuration reader
from config import config
import pymysql
import os
import time


class DbWriter(ListWriter):
    """
    Writes to a db, connection string in the dbConfig file
    """

    dbName = ''
    dbConfigFile = ''
    monitor_interval = 50

    def __init__(self, configInfo):
        super().__init__(configInfo)
        '''Set up dbConfig'''
        try:
            args: list = self.oConfig.drsDbConfig.split(':')
            self.dbName = args[0]
            self.dbConfigFile = os.path.expanduser(args[1])
        except IndexError:
            raise IndexError('Invalid argument: Must be formatted as section:file ')

    def write_list(self, srcList):
        """
        @summary: emits a list into the configured database
        @param srcList: Comma separated list of values

        Requires self.oConfig.sproc to exist
        """

        hadBarf = False
        # Load the db configuration from the file given in
        #

        cfg = config.DBConfig(self.dbName, self.dbConfigFile)
        # cfg = dbConfig.DBConfig('dev', self.oConfig.drsDbConfig)
        dbConnection = self.start_connect(cfg)

        with dbConnection:
            curs = dbConnection.cursor()
            total = len(srcList)
            calls = 0
            etnow = time.perf_counter()
            try:
                for aVal in srcList:
                    try:
                        aval_type = type(aVal)
                        # hack to handle strings and other data types separately
                        if aval_type is str:
                            curs.callproc(self.oConfig.sproc, (aVal.strip(),))
                        if aval_type is dict or aval_type is list:
                            curs.callproc(self.oConfig.sproc, tuple(aVal))
                        if aval_type is tuple:
                            curs.callproc(self.oConfig.sproc, aVal)

                        calls += 1
                        if calls % self.monitor_interval == 0:
                            y = time.perf_counter()
                            print(" %d calls ( %3.2f %%).  Rate: %5.2f /sec"
                                  % (calls, 100 * calls / total, self.monitor_interval / (y - etnow)))
                            etnow = y

                    # Some outlines are not in unicode
                    except UnicodeEncodeError:
                        print(':{0}::{1}:'.format(aVal[0].strip(),
                                                  aVal[1].strip()))
                        pass
                    except Exception:
                        hadBarf = True
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        print(exc_type)
                        if dbConnection is not None:
                            dbConnection.rollback()
                        raise

            finally:
                if not hadBarf:
                    dbConnection.commit()
                if curs is not None:
                    curs.close()

    def test(self):
        cfg = config.DbConfig(self.dbName, self.dbConfigFile)
        self.start_connect(cfg)

    @staticmethod
    def start_connect(cfg):
        """
        @summary: Creates the db connection from the configuration
        """
        return pymysql.connect(read_default_file=cfg.db_cnf,
                               read_default_group=cfg.db_host,
                               charset='utf8')

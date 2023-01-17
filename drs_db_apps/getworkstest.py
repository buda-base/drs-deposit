"""
Created on Mar 13, 2018
This is a basic skeleton which shows how to locate a dbConfig file,
and start a connection to its db.

@author: jsk
"""
from pathlib import Path
import sys
from config import config
import pymysql


def getworkstest():
    """
    Read the remote database from a dbConfig and  connect to it
    """

    # Read the path. This library's client programs pass this in as a parm:
    # --d dev:drsBatch
    # which is a shorthand for ../../../conf/drsBatch.dbConfig.
    # See dbConfig.DbConfig
    cfgPath = Path(__file__).parent.parent / 'conf' / 'drsBatch.dbConfig'
    if cfgPath.is_file():
        print('yes')
    cfg = config.DBConfig('prod', str(cfgPath))

    myConnection = pymysql.connect(read_default_file=cfg.db_cnf,
                                   read_default_group=cfg.db_host,
                                   db='drs',

                                   charset='utf8')
    #
    with myConnection.cursor() as cursor:
        backSet = cursor.execute('select * from Outlines limit 10;')
        results = cursor.fetchall()
        for res in results:
            print(res)


if __name__ == '__main__':
    getworkstest()

'''
Created on Mar 6, 2018

@author: jsk
'''
# base class
from OutlineWrite.listwriter import ListWriter

# Configuration reader
from Config.config import DbConfig
import pymysql
from Config import readcfg_test


class DbWriter(ListWriter):
    '''
    Writes to a db, connection string in the config file
    '''

    def write_list(self, srcList):
        
        dbConnection = None
        curs = None
        hadBarf = False
        try:
        # Load the db configuration from the file
            cfg = DbConfig('dev', self.oConfig)
            dbConnection = self.start_connect(cfg)
            
            with dbConnection:
                curs = dbConnection.cursor()

                for aVal in srcList:
                    try:
                        curs.callproc('AddOutline', (aVal[0].strip(), aVal[1].strip()))
                    except UnicodeEncodeError:
                        print(':{0}::{1}:'.format(aVal[0].strip(), aVal[1].strip()))
                        pass 
                    
                curs.close()
                curs = None
        # Some outlines are not in unicode
            
        except Exception:
            hadBarf = True
            if dbConnection is not None:
                dbConnection.rollback()
            raise
                    
        finally:
            if not hadBarf:
                dbConnection.commit()
            if curs is not None:
                curs.close()
            if dbConnection is not None:
                dbConnection.close()
        
    def start_connect(self, cfg):
        '''
        @summary: Creates the db connection from the configuration
        '''
        return pymysql.connect(host=cfg.host,
                               user=cfg.user,
                               password=cfg.voldeMort,
                               port=cfg.port,
                               db=cfg.schema,
                               charset='utf8')
        

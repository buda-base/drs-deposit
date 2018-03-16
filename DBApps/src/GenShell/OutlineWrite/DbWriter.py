'''
Created on Mar 6, 2018

@author: jsk
'''
# base class
from OutlineWrite.listwriter import ListWriter

# Configuration reader
from DBApp import config
import pymysql



class DbWriter(ListWriter):
    '''
    Writes to a db, connection string in the config file
    '''

    def write_list(self, srcList):
        '''
        @summary: emits a list into the configured database
        @param srcList: Comma separated list of values
        
        Requires self.oConfig.sproc to exist
        '''
        
        dbConnection = None
        curs = None
        hadBarf = False
        try:
        # Load the db configuration from the file given in 
            cfg = config.DBConfig('dev', self.oConfig.drsDbConfig)
            dbConnection = self.start_connect(cfg)
            
            with dbConnection:
                curs = dbConnection.cursor()

                for aVal in srcList:
                    try:
                        curs.callproc(self.oConfig.sproc, (aVal[0].strip(), aVal[1].strip()))
                        
                    # Some outlines are not in unicode
                    except UnicodeEncodeError:
                        print(':{0}::{1}:'.format(aVal[0].strip(), aVal[1].strip()))
                        pass 
                    
                curs.close()
                curs = None
            
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
        
    def test(self,cfg):
            cfg = DbConfig('dev', self.oConfig.db)
            dbConnection = self.start_connect(cfg)
        
    def start_connect(self, cfg):
        '''
        @summary: Creates the db connection from the configuration
        '''
        return pymysql.connect(read_default_file = cfg.db_cnf,
                               read_default_group = cfg.db_host,
                               charset='utf8')
        

'''
Created on Mar 6, 2018

@author: jsk
'''
from OutlineWrite import listwriter
import Config

class DbWriter(listwriter):
    '''
    base class of writer objects
    '''

 
    def __init__(self, configObj):
        '''
        Constructor:
        :param configObj: io path to a config file. See configparser
        for format
        '''            
        self.oConfig = configObj
        
    def getConfigValues(self):
        cfg=Config(self.oConfig)
        print(cfg.dbs.dev.host)
        
        

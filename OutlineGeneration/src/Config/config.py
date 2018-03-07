'''
Created on Mar 7, 2018

@author: jsk
'''
import configparser

class DbConfig(object):
    """
    :summary: Loads a db section from the named config file
    :param dbName: section in the outlineGen.config
    :param configFile: Path to config file
    """    
    
    def __init__(self,dbName,configFile):
        """
        :param dbName: section in the outlineGen.config
        :param configFile: Path to config file
        """
        self._section = dbName; 
        self._config = configparser.ConfigParser()
        self._config.read(configFile)
    
    '''
    host - read only
    '''
    @property
    def host(self):
        return self._config[self._section]['server']
        

    
    
        
        
    

"""
Created on Mar 7, 2018

Wrapper for a dbConfig file whose format is
[mysql]
mySqlCnfPath = "a MySql conformant dbConfig file"

[dbName1]
server = <section in the file specified in [mysql]['mySqlCnfPath']

[dbName2]
server = ....
[...]

Abstracts the databases into aliases, e.g. [dev] [qa], [prod]

@author: jsk

Properties:
"""
import configparser
import os
from pathlib import Path
from builtins import property


class DBConfig:
    """
    :summary: Prepares mySql connector option semi securely
    :param dbName: section in the DbApp file
    :param configFile: Path to DbAppConfig file
    
    """

    def __init__(self, dbName=None, configFileName=None):
        """
        
        """
        if dbName is not None:
            self.db_alias = dbName
        if configFileName is not None:
            self.config_file_name = os.path.expanduser(configFileName)

    '''
    Server - read only
    '''

    @property
    def db_host(self):
        """ De alias db_alias """
        self.test_init()
        return self._configParser[self.db_alias][self.__serverKey]

        # --------------------------------------------------------------------------

    @property
    def db_cnf(self):
        """    MySQL ConfigFile - read only    """
        self.test_init
        return self._configParser[self.__cnfFileSection][self.__cnfKey]
        # --------------------------------------------------------------------------

    @property
    def config_file_name(self):
        """Config file we are parsing"""
        return self._configFQPath

    # --------------------------------------------------------------------------
    @config_file_name.setter
    def config_file_name(self, value):
        """Set the name of the DbAppConfig file"""
        cfgPath = Path(value)
        if cfgPath.is_file():
            self._configFQPath = str(cfgPath)
            # Rebuild the _parser
            self._parser(self._configFQPath)
        else:
            # On error, keep existing value
            raise FileNotFoundError(str(cfgPath))

    # --------------------------------------------------------------------------
    #
    # Public property db_alias: which dbConfig dbConfig name you want
    @property
    def db_alias(self):
        """The _parser dbConfig file's server section"""
        return self._serverSection

    @db_alias.setter
    def db_alias(self, value):
        self._serverSection = value

    # --------------------------------------------------------------------------
    def _parser(self, fileName):
        """
        Creates a dbConfig _parser from fileName
        """
        self._configParser = configparser.ConfigParser()
        self._configParser.read(fileName)

    # --------------------------------------------------------------------------
    def test_init(self):
        """Tests for variable setup before action"""
        if not self.db_alias \
                or not self.__serverKey \
                or not self.__cnfFileSection \
                or not self._configParser \
                or not self.__cnfKey:
            raise ValueError

            #

    # private variables
    _configFQPath = None
    _configParser = None
    _serverSection = None
    __serverKey = 'server'
    __cnfFileSection = 'mysql'
    __cnfKey = 'mySqlCnfPath'

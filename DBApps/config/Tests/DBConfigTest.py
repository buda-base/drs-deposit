"""
Created on Mar 14, 2018

@author: jsk
"""
import unittest

import os

from config import config


def brackets(contents):
    return '[' + str(contents) + ']'


class TestHappyPath(unittest.TestCase):
    __goodFile = "DbConfigHappyTest"
    # Doesnt have to be a valid file. 
    __expectedMySqlConfigFile = "HibbityHabbityHoopstyfreen"
    __expectedSection1 = 'section1'
    __expectedSection1Value = 'somethingOrOther'
    # These lifted from dbConfig.py
    __serverKey = 'server'
    __cnfFileSection = 'mysql'
    __cnfKey = 'mySqlCnfPath'

    def setUp(self):
        """
        Create a conforming dbConfig file
        """

        with open(self.__goodFile, "w") as cfg:
            cfg.write("%s\n" % "# Shouldnt matter")
            cfg.write("%s\n" % brackets(self.__cnfFileSection))
            cfg.write("%s = %s\n" % (self.__cnfKey, self.__expectedMySqlConfigFile))
            cfg.write("%s\n" % '\n')
            cfg.write("%s\n" % brackets(self.__expectedSection1))
            cfg.write("%s = %s\n" % (self.__serverKey, self.__expectedSection1Value))

    def tearDown(self):
        # Pack it in, pack it out
        os.unlink(self.__goodFile)
        pass

    def testDbConfigNoParams(self):
        # Arrange
        x = config.DBConfig()
        x.config_file_name = self.__goodFile
        x.db_alias = self.__expectedSection1
        # Act
        # Assert
        self.assertEqual(x.db_host, self.__expectedSection1Value)

    def testDbConfigOneParams(self):
        x = config.DBConfig(dbName=self.__expectedSection1)
        x.config_file_name = self.__goodFile
        # Act
        # Assert
        self.assertEqual(x.db_host, self.__expectedSection1Value)
        self.assertEqual(x.db_cnf, self.__expectedMySqlConfigFile)

    def testDbConfigParams(self):
        x = config.DBConfig(self.__expectedSection1, self.__goodFile)
        # Act
        # Assert
        self.assertEqual(x.db_host, self.__expectedSection1Value)
        self.assertEqual(x.db_cnf, self.__expectedMySqlConfigFile)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

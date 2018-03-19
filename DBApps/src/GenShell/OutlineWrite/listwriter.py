'''
Created on Mar 6, 2018

@author: jsk
'''
from abc import ABCMeta, abstractmethod
from distutils.sysconfig import _config_vars


class ListWriter(metaclass=ABCMeta):
    '''
    Base class for writing lists
    '''
    '''
    :summary: holds opaque object defining the configuration.
    subclass dependent
    '''
    @property
    def oConfig(self):
        return self._config

    @oConfig.setter
    def oConfig(self, value):
        self._config = value
    '''
    Constructor
    :param config: opaque configuration
    '''
    def __init__(self, configInfo):
        self.oConfig = configInfo

    '''
    :summary: Abstract method to write a list
    '''
    @abstractmethod
    def write_list(self, outData): pass

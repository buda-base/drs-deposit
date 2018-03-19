'''
Created on Jan 5, 2018

@author: TBRC-jimk

:summary  named tuple:  errorId searchText parserFunc
'''

from collections import namedtuple

BBErrorKey = namedtuple('BBErrorKey',
                        'errorId searchText parserFunc printFunc')

'''
Created on Mar 7, 2018

@author: jsk
'''
from pathlib import Path

from Config.config import DbConfig

if __name__ == '__main__':

    my_file = Path("outlineGen.config")
    if my_file.is_file():
        print('yes')
    x = DbConfig('dev','outlineGen.config')
    print(x.host)
    
'''
Created on Mar 13, 2018

@author: jsk
'''
import pathlib

def main(args):
    '''
    Read the remote database from a config and  connect to it
    '''
    cfgPath =  Path(__file__).parent / 'conf' / 'drsBatch.config' 
    if cfgPath.is_file():
        print('yes')
    x = DBConfig('dev',str(cfgPath))
    
if __name__ == '__main__':
    main(args[1:])
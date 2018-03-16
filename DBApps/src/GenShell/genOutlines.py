'''
Created on Mar 6, 2018

@author: jsk
'''
import sys
import argparse

from TBRCSrc import readOutlineXml as xr
from lxml import etree
from OutlineWrite import DbWriter, CSVWriter



class getArgs:
    '''
    Holds command line arguments
    '''
    pass


def main(args):
 
    myArgs= getArgs()
    parseArgs(myArgs)
    
    '''
    @todo: Allow redirect from URI query
    '''

    outlines = get_attr_text_from_file(myArgs.sourceFile,'work','/outlines/outline')
    
    writer = None
    if myArgs.csv is None:
        myArgs.sproc = 'AddOutline'
        writer = DbWriter.DbWriter(myArgs)
    if myArgs.drsDbConfig is None:
        writer = CSVWriter.CSVWriter(myArgs.csv)
    
    writer.write_list(outlines)
        
    
    

def parseArgs(argNamespace):
    '''
    :param argNamespace. class which holds arg values
    '''
    _parser = argparse.ArgumentParser \
    (description='Extracts outline from TBRC wget formatted list of works',\
    usage='%(prog)s \n[-c CSV outputs csv format to file CSV.\n\t \
    | -d --drsDbConfig: Use drs config file to connect to \[arg\] database.]')
    
    _parser.add_argument("sourceFile",help='XML formatted input. Generated from TBRC query')
    
    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--csv')
    group.add_argument('-d','--drsDbConfig')
    
    _parser.parse_args(namespace=argNamespace)
    
def get_attr_text_from_file(inFilePath,attrName,path):
    """Builds a list of the attributes"""
    doc = etree.parse(inFilePath)
    xrr = xr.OutlineReader()
    return xrr.get_attr_text(doc,attrName, path)
    
#
#----------------        MAIN     ------------------------------------
if __name__ == '__main__':
        main(sys.argv[1:])
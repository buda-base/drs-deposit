'''
Created on Mar 6, 2018

@author: jsk
'''
import sys
import argparse
from  OutlineWrite.CSVWriter  import * # We want it all

from TBRCSrc.read import get_attr_text
from lxml import etree
from lxml.html._diffcommand import description



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
        writer = DbWriter(myArgs.db)
    if myArgs.db is None:
        writer = CSVWriter(myArgs.csv)
    
    writer.write_list(outlines)
        
    
    

def parseArgs(argNamespace):
    '''
    :param argNamespace. class which holds arg values
    '''
    parser = argparse.ArgumentParser \
    (description='Extracts outline from TBRC wget formatted list of works',\
    usage='%(prog)s \n[-c CSV outputs csv format to file CSV.\n\t | -d DB outputs to db whose parameters are given in config file DB ]')
    
    parser.add_argument("sourceFile",help='XML formatted input. Generated from TBRC query')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--csv')
    group.add_argument('-d','--db')
    
    parser.parse_args(namespace=argNamespace)
    
def get_attr_text_from_file(inFilePath,attrName,path):
    """Builds a list of the attributes"""
    doc = etree.parse(inFilePath)
    return get_attr_text(doc,attrName, path)
    



if __name__ == '__main__':
        main(sys.argv[1:])
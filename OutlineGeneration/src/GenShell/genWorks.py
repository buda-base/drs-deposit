'''
Created on Mar 8, 2018

@author: jsk
'''

import sys
import argparse
import fileinput

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

    outlines = []
    with fileinput.input(files=(myArgs.sourceFile)) as f:
        [ outlines.append( process(someLine))  for someLine in f ]
    
    writer = None
    if myArgs.csv is None:
        myArgs.sproc = 'AddWork'
        writer = DbWriter.DbWriter(myArgs)
    if myArgs.db is None:
        writer = CSVWriter.CSVWriter(myArgs.csv)
    
    writer.write_list(outlines)
        
    
def listFromFile(inFilePath):
    '''
    @summary: Creates a list object from a csv file with two columns
    @param inFilePath: source file
    '''
   
                
        

def parseArgs(argNamespace):
    '''
    :param argNamespace. class which holds arg values
    '''
    parser = argparse.ArgumentParser \
    (description='Replicates work HOLLIS pair file',\
    usage='%(prog)s \n[-c CSV outputs csv format to file CSV.\n\t | -d DB outputs to db whose parameters are given in config file DB ]')
    
    parser.add_argument("sourceFile",help='CSV file containing Work, HOLLIS tuples (no heading)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c','--csv')
    group.add_argument('-d','--db')
    
    parser.parse_args(namespace=argNamespace)
    
#
#----------------        MAIN     ------------------------------------

def process(textLine):
    '''
    @summary adds a two column, comma separated line to a list of tuples
    @param textLine: source
    '''
    beads = textLine.split(',')
    if len(beads) >= 2:
        return beads[0],beads[1]
    
if __name__ == '__main__':
        main(sys.argv[1:])
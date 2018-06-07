'''
Created on Mar 8, 2018

@author: jsk
'''

import argparse
import csv
import sys
from GenShell.Writers.CSVWriter import CSVWriter
from GenShell.Writers.DbWriter import DbWriter


class getArgs:
    """
    Holds command line arguments
    """
    pass


def main(args):

    myArgs = getArgs()
    parseArgs(myArgs)

    '''
    @todo: Allow redirect from URI query
    '''

    outlines = csv_to_list(myArgs.sourceFile)
    writer = None
    if myArgs.csv is None:
        myArgs.sproc = 'AddWork'
        writer = DbWriter(myArgs)
    if myArgs.drsDbConfig is None:
        writer = CSVWriter(myArgs.csv)

    writer.write_list(outlines)


def csv_to_list( file_name: str) -> list:

    rc = []
    with open(file_name, newline='\n', encoding='utf-8') as csvfile:
        rdr = csv.DictReader(csvfile, dialect='unix')
        for row in rdr:
            rc.append((row['RID'], row['HOLLIS']))
    return rc

def parseArgs(argNamespace):
    '''
    :param argNamespace. class which holds arg values
    '''
    _parser = argparse.ArgumentParser(description='Replicates work HOLLIS\
     pair file', usage='%(prog)s \n[-c CSV outputs csv format to file CSV.\n\t\
     | -d DBAppSection:DbAppFile outputs to db whose parameters are given in \n\t\
     config file \'DbAppFile\' which contains section \'DbAppSection\'')

    _parser.add_argument("sourceFile", help='CSV file containing Work, \
    HOLLIS tuples with headings \'RID\' and \'HOLLIS\'')
    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--csv')
    group.add_argument('-d', '--drsDbConfig')

    _parser.parse_args(namespace=argNamespace)

#
# ----------------        MAIN     ------------------------------------


def process(textLine):
    '''
    @summary adds a two column, comma separated line to a list of tuples
    @param textLine: source
    '''
    beads = textLine.split(',')
    if len(beads) >= 2:
        return beads[0], beads[1]


if __name__ == '__main__':
        main(sys.argv[1:])

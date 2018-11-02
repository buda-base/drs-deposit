"""
Created on Mar 8, 2018

@author: jsk
"""

import argparse
import csv
import sys
from DBApps.Writers.CSVWriter import CSVWriter
from DBApps.Writers.DbWriter import DbWriter


class GetWorksArgs:
    """
    Holds command line arguments
    """
    pass


def genWorks():
    myArgs = GetWorksArgs()
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

    try:
        writer.write_list(outlines)
    except:
        tt, value, tb = sys.exc_info()

        import traceback
        print
        {'exception_value': value,
         'value': tt,
         'tb': traceback.format_exception(tt, value, tb)}



def csv_to_list(file_name: str) -> list:
    rc = []
    with open(file_name, newline='\n', encoding='utf-8') as csvfile:
        rdr = csv.DictReader(csvfile, dialect='unix')
        for row in rdr:
            rc.append((row['RID'], row['HOLLIS']))
    return rc


def parseArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Replicates work HOLLIS\
     pair file', usage='%(prog)s \n[-c CSV outputs csv format to file CSV.\n\t\
     | -d DBAppSection:DbAppFile outputs to db whose parameters are given in \n\t\
     dbConfig file \'DbAppFile\' which contains section \'DbAppSection\'')

    _parser.add_argument("sourceFile", help='CSV file containing Work, \
    HOLLIS tuples with headings \'RID\' and \'HOLLIS\'')
    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--csv')
    group.add_argument('-d', '--drsDbConfig')

    _parser.parse_args(namespace=argNamespace)


#-----------------        VOLUMES  ------------------------------------

def parseVolumeArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Replicates work HOLLIS\
     pair file', usage='%(prog)s [-c CSV outputs csv format to file CSV.  -d DBAppSection:DbAppFile outputs to db whose parameters are given in dbConfig file \'DbAppFile\' which contains section \'DbAppSection\'')

    _parser.add_argument("rootFolder", help='Parent of the directories in folderList')
    _parser.add_argument("folderFile", help='file containing folders to populate volumes.')
    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--csv')
    group.add_argument('-d', '--drsDbConfig')

    _parser.parse_args(namespace=argNamespace)


def genVolumes():
    """
    Populates volumes for a list of folders
    :return:
    """
    pass

#
# ----------------        MAIN     ------------------------------------


def process(textLine):
    """
    @summary adds a two column, comma separated line to a list of tuples
    @param textLine: source
    """
    beads = textLine.split(',')
    if len(beads) >= 2:
        return beads[0], beads[1]

# RELM
if __name__ == '__main__':
    genWorks()

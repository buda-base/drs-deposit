"""
Created on Mar 8, 2018

@author: jsk
"""

import argparse
import csv
import sys
from Writers.CSVWriter import CSVWriter
from Writers.DbWriter import DbWriter


class GetWorksArgs:
    """
    Holds command line arguments
    """
    pass


def gen_works():
    my_args = GetWorksArgs()
    parse_args(my_args)

    '''
    @todo: Allow redirect from URI query
    '''

    outlines = csv_to_list(my_args.sourceFile)
    writer = None
    if my_args.csv is None:
        my_args.sproc = 'AddWork'
        writer = DbWriter(my_args)
    if my_args.drsDbConfig is None:
        writer = CSVWriter(my_args.csv)

    try:
        writer.write_list(outlines)
    except IOError:
        tt, value, tb = sys.exc_info()

        import traceback
        print(
            {'exception_value': value,
             'value': tt,
             'tb': traceback.format_exception(tt, value, tb)})


def csv_to_list(file_name: str) -> list:
    rc = []
    with open(file_name, newline='\n', encoding='utf-8') as csvfile:
        rdr = csv.DictReader(csvfile, dialect='unix')
        for row in rdr:
            rc.append((row['RID'], row['HOLLIS']))
    return rc


def parse_args(arg_namespace):
    """
    :param arg_namespace. class which holds arg values
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

    _parser.parse_args(namespace=arg_namespace)


# -----------------        VOLUMES  ------------------------------------

def parse_volume_args(arg_namespace):
    """
    :param arg_namespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Replicates work HOLLIS pair file',
                                      usage='%(prog)s [-c CSV outputs csv format to file CSV.  -d '
                                            'DBAppSection:DbAppFile outputs to db whose parameters are given in '
                                            'dbConfig file \'DbAppFile\' which contains section \'DbAppSection\'')

    _parser.add_argument("rootFolder", help='Parent of the directories in folderList')
    _parser.add_argument("folderFile", help='file containing folders to populate volumes.')
    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--csv')
    group.add_argument('-d', '--drsDbConfig')

    _parser.parse_args(namespace=arg_namespace)


def gen_volumes():
    """
    Populates volumes for a list of folders
    :return:
    """
    pass


#
# ----------------        MAIN     ------------------------------------


def process(text_line):
    """
    @summary adds a two column, comma separated line to a list of tuples
    @param text_line: source
    """
    beads = text_line.split(',')
    if len(beads) >= 2:
        return beads[0], beads[1]


if __name__ == '__main__':
    gen_works()

"""
Created on Mar 6, 2018

@author: jsk

Generates outlines from a saved xml file which is the output
of https://legacy.tbrc.org/public?module=outlines&query=outline&arg=
(see DBApps/conf/drsBatch.config)(
"""
import argparse

from lxml import etree

from TBRCSrc import readOutlineXml as ReadXml
from Writers import DbWriter, CSVWriter


class GetOutlineArgs:
    """
    Holds command line arguments
    """
    pass


def gen_outlines():
    my_args = GetOutlineArgs()
    parse_args(my_args)

    '''
    @todo: Allow redirect from URI query
    '''

    # take 2: just use a list
    outlines = get_attr_text_from_file(my_args.sourceFile,
                                       'work', '/outlines/outline')
    #  outlines = []
    #  with open(myArgs.sourceFile,'r') as wks:
    #      for wk in wks:
    #          outlines.append(wk.rstrip('\n'))

    writer = None
    if my_args.csv is None:
        my_args.sproc = 'AddOutline'
        writer = DbWriter.DbWriter(my_args)
    if my_args.drsDbConfig is None:
        writer = CSVWriter.CSVWriter(my_args.csv)

    writer.write_list(outlines)


def parse_args(arg_namespace):
    """
    :param arg_namespace. class which holds arg values
    populates argNamespace with
    .csv
    .drsDbConfig
    string properties
    """
    _parser = argparse.ArgumentParser(
        description='Extracts outline from\
                                       TBRC wget formatted list of works',
        usage='%(prog)s \n[-c --csv csvFileOutPath outputs csv\
                                       format to output.\n\t | -d \
                                       --drsDbConfig  section:cfgFileName  Use drs dbConfig file to \
                                       connect to \'section\' section in \'cfgFile\' database.]')

    _parser.add_argument("sourceFile", help='XML formatted input. \
    Generated from TBRC query')

    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--csv')
    group.add_argument('-d', '--drsDbConfig')

    _parser.parse_args(namespace=arg_namespace)


def get_attr_text_from_file(infile_path, attr_name, path):
    """Builds a list of the attributes"""
    doc = etree.parse(infile_path)
    xrr = ReadXml.OutlineReader()
    return xrr.get_attr_text(doc, attr_name, path)


#

# ----------------        MAIN     ------------------------------------


if __name__ == '__main__':
    gen_outlines()

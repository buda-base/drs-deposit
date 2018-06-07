"""
Created on Mar 6, 2018

@author: jsk
"""
import sys
import argparse

from GenShell.TBRCSrc import readOutlineXml as xr
from lxml import etree
from GenShell.Writers import DbWriter, CSVWriter


class getArgs:
    '''
    Holds command line arguments
    '''
    pass


def main(args):
    myArgs = getArgs()
    parseArgs(myArgs)

    '''
    @todo: Allow redirect from URI query
    '''

   # take 2: just use a list outlines = get_attr_text_from_file(myArgs.sourceFile,
   #                                    'work', '/outlines/outline')
    outlines = []
    with open(myArgs.sourceFile,'r') as wks:
        for wk in wks:
            outlines.append(wk.rstrip('\n'))



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
    populates argNamespace with
    .csv
    .drsDbConfig
    string properties
    '''
    _parser = argparse.ArgumentParser(
                                      description='Extracts outline from\
                                       TBRC wget formatted list of works',
                                      usage='%(prog)s \n[-c --csv csvFileOutPath outputs csv\
                                       format to output.\n\t | -d \
                                       --drsDbConfig  section:cfgFileName  Use drs config file to \
                                       connect to \'section\' section in \'cfgFile\' database.]')

    _parser.add_argument("sourceFile", help='XML formatted input. \
    Generated from TBRC query')

    group = _parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--csv')
    group.add_argument('-d', '--drsDbConfig')

    _parser.parse_args(namespace=argNamespace)


def get_attr_text_from_file(inFilePath, attrName, path):
    """Builds a list of the attributes"""
    doc = etree.parse(inFilePath)
    xrr = xr.OutlineReader()
    return xrr.get_attr_text(doc, attrName, path)

#

# ----------------        MAIN     ------------------------------------


if __name__ == '__main__':
        main(sys.argv[1:])

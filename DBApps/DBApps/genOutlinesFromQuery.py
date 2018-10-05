"""
Created on Mar 6, 2018

@author: jsk

Generates outlines from a saved xml file which is the output
of https://www.tbrc.org/public?module=outlines&query=outline&arg=
(see DBApps/conf/drsBatch.config)(
"""
import sys
import argparse

from DBApps.TBRCSrc import readOutlineXml as ReadXml
from lxml import etree
from DBApps.Writers import DbWriter, CSVWriter


class GetOutlineArgs:
    """
    Holds command line arguments
    """
    pass


def genOutlines():
    myArgs = GetOutlineArgs()
    parseArgs(myArgs)

    '''
    @todo: Allow redirect from URI query
    '''

    # take 2: just use a list
    outlines = get_attr_text_from_file(myArgs.sourceFile,
                                       'work', '/outlines/outline')
    #  outlines = []
    #  with open(myArgs.sourceFile,'r') as wks:
    #      for wk in wks:
    #          outlines.append(wk.rstrip('\n'))

    writer = None
    if myArgs.csv is None:
        myArgs.sproc = 'AddOutline'
        writer = DbWriter.DbWriter(myArgs)
    if myArgs.drsDbConfig is None:
        writer = CSVWriter.CSVWriter(myArgs.csv)

    writer.write_list(outlines)


def parseArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
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

    _parser.parse_args(namespace=argNamespace)


def get_attr_text_from_file(inFilePath, attrName, path):
    """Builds a list of the attributes"""
    doc = etree.parse(inFilePath)
    xrr = ReadXml.OutlineReader()
    return xrr.get_attr_text(doc, attrName, path)


#

# ----------------        MAIN     ------------------------------------


if __name__ == '__main__':
    genOutlines()

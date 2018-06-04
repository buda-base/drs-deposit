"""
Read a csv of DRS deposit log entries, extract fields for call to DRS db
sproc 'AddDRS'

"""
import fileinput
import sys

import argparse

from GenShell.Writers.DbWriter import DbWriter


def process(text_line):
    """
    Returns a comma separated string containing the required parameters to DRSUpdate
    :param text_line:
    :return:
    """


def main(args):

    myArgs: object
    parseArgs(myArgs)

    outlines = []
    with fileinput.input(files=(myArgs.sourceFile)) as f:
        [outlines.append(process(someLine)) for someLine in f]

    writer = None
    myArgs.sproc = "AddDRS"
    writer = DbWriter(myArgs)
    writer.write_list(outlines)

def parseArgs(argNamespace: object) -> object:
    """
    :rtype: object
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser\
        (description="Reads  a raw CSV file which holds output of a HUL DRS \
                     WebAdmin search", usage="%(prog)s -d section:configFile sourcefile \
                     where 'section' is a section in a python config file 'configFile' ")

    _parser.add_argument("sourceFile", help="CSV file containing search results.")
    _parser.add_argument("-d", "--db")
    _parser.parse_args(namespace=argNamespace)


if __name__ == '__main__':
    main(sys.argv[1:])

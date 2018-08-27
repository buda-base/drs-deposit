#!/usr/bin/env python3
#
# split the WebAdminResults of getReadyWorks into n files, along work boundaries
#
import argparse
import os
import pathlib


class GetSplitWorksArgs:
    """
    Holds command line arguments
    """
    pass


def splitWorks():
    myArgs = GetSplitWorksArgs()
    parseArgs(myArgs)
    testArgs(myArgs)
    do_split(myArgs)


def do_split(args):
    """
    Splits the input file into n segments, breaking along header rows
    :param args:
    :return:
    """
    # Pass 1: count the number of header lines
    headerLine = ''
    with open(args.source, "r") as src:
        headerLine = src.readline()

    # Now count
    nWorks = 0
    with open(args.source, "r") as src:
        for line in src:
            if headerLine in line:
                nWorks += 1

    # And split
    worksPerFile = nWorks / args.numFiles
    if worksPerFile == 0:
        raise ValueError(f"source file {args.source:s} contains fewer works than the number of files. Nothing to do.")

    worksThisFile = 0
    currentFileNumber = 0

    # Save the extension
    base, ext = os.path.splitext(args.source)
    outPath, baseName = os.path.split(base)
    # What did this do, other than mess up
    # an extension:
    # it took allList.txt and made it allList1..t.x.t
    #  if ext:
    #     ext = '.' + ext

    # Writes into same directory
    currentOutFile: object = None
    with open(args.source, "r") as src:
        for srcLine in src:
            if headerLine in srcLine:
                worksThisFile += 1
                if worksThisFile > worksPerFile or currentOutFile is None:
                    # write the remainder to the last file
                    if currentFileNumber < args.numFiles:
                        if currentOutFile is not None:
                            currentOutFile.close()
                        currentFileNumber += 1
                        worksThisFile = 1
                        # Works on win, not on mac
                        # currentOutFile = open(buildOutPath(outPath, baseName, currentFileNumber, ext), "w")
                        # Done: See if this works on win. Works on MAC
                        currentOutFile = buildOutPath(outPath, baseName, currentFileNumber, ext).open("w")

            currentOutFile.write(srcLine)


def buildOutPath(outPath, baseName, currentFileNumber, ext):
    """
    Builds a path out of a set of values
    :param outPath:
    :param baseName:
    :param currentFileNumber:
    :param ext:
    :return:
    """
    return pathlib.Path(outPath) / f'{baseName:s}{currentFileNumber:d}{ext:s}'


def parseArgs(argNamespace):
    """
    :param argNamespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser(description='Splits the output of getReadyWorks.py into separate files, named '
                                                  'inputfile01, 02, ....',
                                      usage="%(prog)s | -n n How many works split.",
                                      epilog='Contents not guaranteed to be equal lengths '
                                             'but they will contain an equal number of works, as much as '
                                             'possible. ** Warning ** first line of file is the header line which '
                                             'this program assumes is the text of the boundary between works.'
                                      )
    _parser.add_argument('-n', '--numFiles', help='how many output files to create', type=int,
                         default=10, choices=range(1, 9999999))
    _parser.add_argument("source", help='Input source')

    _parser.parse_args(namespace=argNamespace)


def testArgs(args):
    """
    Tests arguments for sanity:
    - numFiles is a positive number
    :param args:
    :return:
    """
    if args.numFiles < 2:
        raise ValueError("Number of files must be greater than one.")


if __name__ == '__main__':
    splitWorks()

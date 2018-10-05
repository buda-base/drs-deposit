#!/usr/bin/env python3

"""
Entry point for getting related files.
"""
from DBApps.readyRelated import ReadyRelated, ReadyRelatedParser
from DBApps.DbAppParser import DbArgNamespace
from DBApps.Writers.CSVWriter import CSVWriter


def SetupParse() -> object:
    """
    Sets up and parses sys.argv arguments
    :return: arguments parsed into options. Should have members:
    outline (bool)
    printmaster (bool)
    maxWorks (int)
    resultsPath: path to file where the directory exists (execution directory
    if none listed
    """
    p = ReadyRelatedParser(description="Fetch Works information which have outlines or print masters",
                           usage=" [ -o --outline | -p --printmaster ] -n maxWorks (default = 200) resultsPath")
    return p.parsedArgs


def PutResults(fileName: str, results: list, expectedColumns: list) -> None:
    """
    Write results to file
    :param fileName: resulting path
    :param results: Data to output
    :param expectedColumns: subset of results columns to output
    :return:
    """
    # and write
    myCsv = CSVWriter(fileName)
    myCsv.PutResultSets(results, expectedColumns)


def GetReadyRelated():
    """
    Entry point for getting Related files, either outlines or print masters
    :return:
    """
    rrArgs: DbArgNamespace = SetupParse()
    rr = ReadyRelated(rrArgs)
    sproc = f'GetReady{rr.TypeString}'
    myrs = rr.GetSprocResults(sproc, rrArgs.numResults)
    PutResults(rrArgs.results, myrs, rr.ExpectedColumns)


if __name__ == "__main__":
    GetReadyRelated()

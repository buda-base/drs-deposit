#!/usr/bin/env python3
"""
Entry point for getting ready works' volumes
"""

from DBApps.readyWorks import GetReadyWorks, GetReadyWorksParser
from DBApps.DbAppParser import DbArgNamespace
from DBApps.Writers.CSVWriter import CSVWriter


def SetupParse() -> object:
    p = GetReadyWorksParser(
        description='Downloads ready works to folder, creating files related to folder',
        usage="%(prog)s | -d DBAppSection:DbAppFile [ -n default(200) ] resultPath")
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
    myCsv.write_dict(results, expectedColumns)


def getReadyWorks():
    """
    Entry point for getting works
    :return:
    """
    grArgs: DbArgNamespace = SetupParse()
    gr = GetReadyWorks(grArgs)
    myrs: list = gr.GetSprocResults('GetReadyVolumes', grArgs.numWorks)
    PutResults(grArgs.resultsPath, myrs, gr.ExpectedColumns)


if __name__ == '__main__':
    getReadyWorks()

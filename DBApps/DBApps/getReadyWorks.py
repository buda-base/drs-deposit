#!/usr/bin/env python3
"""
Entry point for getting ready works' volumes
"""

from DBApps.DbAppParser import DbArgNamespace
from DBApps.Writers.CSVWriter import CSVWriter
from DBApps.readyWorks import GetReadyWorks, GetReadyWorksParser


def SetupParse() -> object:
    p = GetReadyWorksParser(
        description='Downloads ready works to folder, creating files related to folder',
        usage="%(prog)s | -d DBAppSection:DbAppFile [ -n default(200) ] resultPath")
    return p.parsedArgs


def getReadyWorks():
    """
    Entry point for getting works
    :return:
    """
    grArgs: DbArgNamespace = SetupParse()
    gr = GetReadyWorks(grArgs)
    myrs: list = gr.GetSprocResults('GetReadyVolumes', grArgs.numWorks)
    csvOut = CSVWriter(grArgs.resultsPath)
    csvOut.PutResultSets(myrs, gr.ExpectedColumns)


if __name__ == '__main__':
    getReadyWorks()

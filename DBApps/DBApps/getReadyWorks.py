#!/usr/bin/env python3
"""
Entry point for getting ready works' volumes
"""
import pathlib

from DBApps.readyWorks import GetReadyWorks, GetReadyWorksParser
from DBApps.DbAppParser import DbArgNamespace
from DBApps.Writers.CSVWriter import CSVWriter
import csv


def SetupParse() -> object:
    p = GetReadyWorksParser(
        description='Downloads ready works to folder, creating files related to folder',
        usage="%(prog)s | -d DBAppSection:DbAppFile [ -n default(200) ] resultPath")
    return p.parsedArgs


def PutResults(fileName: str, results: list, fieldNames: list) -> None:
    """
    Write results to file
    :param fileName: resulting path
    :param results: list of list of dicts
    :param fieldNames: subset of results columns to output
    :return:
    """
    # and write

        # Build the output path
    outfile: pathlib.Path = pathlib.Path(fileName)
    with outfile.open("w", newline='') as fw:
        # Create the CSV writer. NOTE: multiple headers are written to the
        # one output file
        csvwr = csv.DictWriter(fw, fieldNames)
        for resultSet in results:
            if len(resultSet) > 0:
                csvwr.writeheader()
                for resultRow in resultSet:
                    down_row = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                    csvwr.writerow(down_row)


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

"""
Entry point for getting related files.
"""
from DBApps.readyRelated import ReadyRelated, ReadyRelatedParser


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

def GetReadyRelated():
    """
    Entry point for getting Related files, either outlines or printmasters
    :return:
    """
    rrArgs = SetupParse()
    rr = ReadyRelated(rrArgs)
    myrs = rr.GetResults()
    rr.PutResults(rrArgs.results, myrs)


if __name__ == "__main__":
    GetReadyRelated()

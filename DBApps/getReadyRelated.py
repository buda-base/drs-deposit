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
                           usage=" -o --outline | -p --printmaster -n maxWorks (default = 200) resultsPath")
    return p.parsedArgs


if __name__ == "__main__":
    rrArgs = SetupParse()
    Urgylem = ReadyRelated(rrArgs)
    myrs = Urgylem.GetResults()
    Urgylem.PutResults(rrArgs.results, myrs)


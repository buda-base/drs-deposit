# from ErrorFiltering import BBErrorKey


def dumpFunc(errors, errorCollection):
    '''
    foundDumpFunc
    Prints a list of errors found in a file cited in the errorCollection.
    Optimized to assume multiple lines per file.
    but not any error text.

    DbArgNamespace:

    currentError:  BBErrorKey for current error
    error collection:  error instances list
    '''
    print(f"{errors.errorId}\t{errors.searchText}\t")
    for work in errorCollection:
        print(f"\t\t{work}")
    lastFile = ""

    errorsByFile = {}
    for errorLine in errorCollection:
        errorBeads = errorLine.split(':')
# is this error in a different log file?
# If so, start a new list
        foundFile = errorBeads[0]
        foundLine = int(errorBeads[1])

        if (foundFile != lastFile):
            lastFile = foundFile

        if lastFile in errorsByFile.keys():
            errorsByFile[lastFile].append(foundLine)
        else:
            errorsByFile[lastFile] = [foundLine]

    # Now open each file and go to the fifth line before the detected line

    # TODO:for consoleLogFile, errors in errorsByFile.items():
    for errFilePath, errLineList in errorsByFile.items():
        lastLineNumber = 0
        errFile = open(errFilePath, 'r')
        for errLineNumber in errLineList:
            # HACK WARNING:
            errLineNumber -= 5

            # read ahead
            for _ in range(errLineNumber - lastLineNumber):
                next(errFile)
            print (errFile.readline())
            lastLineNumber = errLineNumber + 1

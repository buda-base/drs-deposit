from ErrorFiltering import BBError
'''
basic dump function

Args: 
	errorSource: The types of errors
	errorCollection: Dictionary of errors by type
Prints the error description and the "work,"
which is just the error text

'''
def dumpFunc(errors, errorCollection):
	print(f"{errors.errorId}\t{errors.searchText}\t")
		for work in errorCollection[errors.errorId]:
			print(f"\t\t{work}")

'''
fileDumpFunc
Handles case of an error text which contains a file and location,
but not any error text.

Args: errors: One error descriptor
'''
def foundDumpFunc(errors, errorCollection):
	print(f"{errors.errorId}\t{errors.searchText}\t")
	lastFile = ""
	for work in errorCollection[errors.errorId]:
		curFile= work.split('[:'])

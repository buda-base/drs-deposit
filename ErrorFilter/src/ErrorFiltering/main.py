#!/usr/bin/python
'''
Created on Jan 5, 2018

@author: jsk
'''

import sys, getopt, os

from ErrorFiltering import errorScanner
from ErrorFiltering.BBErrorKey import BBErrorKey
from ErrorFiltering.errorparsers import WorkThenVolume, EXIFWork, TikaParse	
							
from ErrorFiltering.errorLabels import *

knownErrors = []
"""List of possible errors. Key is a mnemonic constant, value is the text in the 
input which indicates the error. See loadErrors"""

'''
dictionary of key=BBErrorKey.errorId value=[list of work identifiers]
'''


def usage():
		print('isolateBatchErrors.py -i <inputfile> --ifile==<inputfile>')


#------------------------------------------------------------
def main(argv):
	inputFile, _args = parseArgs(argv)
	if not os.path.exists(inputFile):
		usage()
		sys.exit(2)
		
	print ('Input file is "', inputFile)
	
	loadErrors()
	
	errScan = errorScanner.ErrorScanner(knownErrors)
	errors = errScan.Scan(inputFile)
	errByType = invertErrors(errors)
	dumpErrors(knownErrors, errByType)
	x = input('ok?')
	print(x)
	
	
#------------------------------------------------------------
def parseArgs(argv):
	"""Only input argument is -i input file"""
	
	if not argv or (argv.count == 0):
		usage()
		sys.exit(1)
	try:
		opts, args = getopt.getopt(argv, "hi:", ["ifile="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('ErrorFiltering main.py -i <inputfile>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg

	return inputfile, args


def loadErrors():
	"""Build the error dictionary"""

	knownErrors.append(BBErrorKey(FAIL_MODS_ID, FAIL_MODS_CALL, lambda errBead: WorkThenVolume(errBead)))
	knownErrors.append(BBErrorKey(FAIL_EXIF_ID, FAIL_EXIF_STR, lambda errBead: EXIFWork(errBead)))
	knownErrors.append(BBErrorKey(FAIL_TIKA_ID, FAIL_TIKA_STR, lambda errBead: TikaParse(errBead)))
	knownErrors.append(BBErrorKey(FAIL_MULTI_PAGE_TIF_ID, FAIL_MULTI_PAGE_TIF_STR, lambda errBead: TikaParse(errBead)))

	
def invertErrors(errors):
	'''
	Coalesces errors by type. Builds a dictionary whose value is a list of the works which have
	the key's error.
	Parameters:
		errors:  a list of errorBead objects
	'''
	errByType = {}
	
	for anError in errors:	
		k = anError.bbErrorKey
		work, volume = k.parserFunc(anError)
		workVolume = f'{work}-{volume}-'
		if k.errorId in errByType.keys() :			
			errByType[k.errorId].append(workVolume)
		else:
			errByType[k.errorId] = [workVolume]
	return errByType


'''
dump each error class to a file
arguments:  
	errMaster: BBErrorKey list
	errByType dict(str, []) where key is an errorId (errMaster[i].errorId)
'''


def dumpErrors(errMaster, errByType):
	for oneErrorType in errByType:
		foundBBError = None 
		for bbError in errMaster:
			if bbError.errorId == oneErrorType:
				foundBBError = bbError
				break
		if foundBBError is None:
			continue
				
		print(f"{foundBBError.errorId}\t{foundBBError.searchText}\t")
		for work in errByType[foundBBError.errorId]:
			print(f"\t\t{work}")
		

if __name__ == "__main__":
	main(sys.argv[1:])

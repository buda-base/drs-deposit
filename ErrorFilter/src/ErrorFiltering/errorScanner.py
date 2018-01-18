'''
Created on Jan 1, 2018

@author: TBRC-jimk
'''
import fileinput
import posixpath
from ErrorFiltering import errorBead


class ErrorScanner:
	"""Scans an input stream for a specific set of error texts.
	The stream is assumed to be in grep -n format:
	filename:line:Other text (which can include the grep delimiter, ':' """
	
	errorResults = []
	lineCount = 0
	
	def __init__(self, errorDict):
		self.errorSources = errorDict

	def Scan(self, inputFilePath):
		"""Scans the file for error patterns and returns the error beads of errors
		we care about"""
		with fileinput.input(files=(inputFilePath)) as f:
			for someLine in f:
				self.process(someLine)
		
		return self.errorResults	
				
	def process(self, aLine):
		"""searches for a set of texts in the line, returns a new error bead"""
		
		lineFrags = aLine.split(':')
		if (len(lineFrags) < 3) :
			return
		
		# the first two fields are just the result of the scan through the bbconsole.txts
		file = lineFrags[0]
		bbConsoleLine = lineFrags[1]
		# We always know the file is bb-console.txt
		_rootPath, bbConsoleHome = posixpath.split(posixpath.dirname(file))
		# dont care about other colon-delimited fields
		# HACK: This removes colons from the raw text. Search strings have to take 
		# this into account
		bbConsoleText = ''.join(lineFrags[2:])
		
		self.lineCount += 1
		
		# TODO Use regexps to speed up
		for anError in iter(self.errorSources):
			# print(f"+ {self.lineCount}__{bbConsoleLine}_|_{bbConsoleText}")
			if anError[1] in bbConsoleText:
				# print(f"found in {bbConsoleLine} {bbConsoleText}")
				self.errorResults.append(errorBead.ErrorBead(bbConsoleHome, bbConsoleLine, anError, bbConsoleText))
			#------------------------------------------------------------- else:
				#------------------------ print(f"NOT found in {bbConsoleLine}")

# 	def lookAheadScan(self,inputFilePath):
# 		"""Scans the file for error patterns and returns the error beads of errors
# 		we care about"""
# 		with fileinput.input(files=(inputFilePath)) as f:
# 				self.lookAheadProcess(f)
# 		
# 		return self.errorResults	
# 		
# 	def lookAheadProcess(self, fileHandle):
# 		"""searches for a set of texts in the line, returns a new error bead"""
# 		keepGoing = True		
# 		while keepGoing: 
# 			aLine = fileHandle.readlines()
# 			lineFrags = aLine.split(':')
# 			if (len(lineFrags) < 3 ) :
# 				continue
# 			
# 			# the first two fields are just the result of the scan through the bbconsole.txts
# 			file=lineFrags[0]
# 			bbConsoleLine=lineFrags[1]
# 			# We always know the file is bb-console.txt
# 			rootPath, bbConsoleHome=posixpath.split(posixpath.dirname(file))
# 			# dont care about other colon-delimited fields
# 			bbConsoleText=''.join(lineFrags[2:])
# 			
# 			self.lineCount += 1
# 			
# 			# TODO Use regexps to speed up
# 			for anError in iter(self.errorSources):
# 				# print(f"+ {self.lineCount}__{bbConsoleLine}_|_{bbConsoleText}")
# 				if anError[1] in bbConsoleText:
# 					print(f"found in {bbConsoleLine} {bbConsoleText}")
# 					self.errorResults.append(errorBead.ErrorBead(bbConsoleHome,bbConsoleLine,anError[0],bbConsoleText))
	

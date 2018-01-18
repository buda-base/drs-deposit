'''
Created on Jan 2, 2018

@author: jsk
'''


class ErrorBead:
	'''
	ErrorBead: base class for error handling
	'''
	file = ''
	lineNumber = ''
	bbErrorKey = None
	'''
	BBErrorKey object
	'''
	errorText = ''
	'''
	Complete error text
	'''
	
	def __init__(self, file, lineNumber, errKey, errText):
		self.file = file
		self.lineNumber = lineNumber
		self.bbErrorKey = errKey
		self.errorText = errText
		

'''
Created on Jan 2, 2018

@author: jsk

	ErrorBead: base class for error handling
'''
class ErrorBead:
	"More pydoc here"

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
		

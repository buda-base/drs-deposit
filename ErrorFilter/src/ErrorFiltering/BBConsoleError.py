'''
Created on Jan 2, 2018

@author: TBRC-jimk

Holds information about error instances in bb-console.txt
'''


class BBConsoleError:
	"""Holds information about error instances in bb-console.txt"""
	
	source = ''
	"""path to file where error was found"""
	
	line = 0
	"""which line held the error"""
	
	work = ''
	"""Which work held the error"""
	
	fullText = ''
	"""Full line of error"""
	

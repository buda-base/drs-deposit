'''
Created on Mar 6, 2018

@author: jsk
'''
import codecs
from OutlineWrite.listwriter import ListWriter

class CSVWriter(ListWriter):
    '''
    Writes a list formatted as a CSV file
    '''


    '''
    Constructor
    :param configInfo is a file to write to: target on disk  
    '''
    def __init__(self,configInfo):
        self.oConfig = configInfo
        

    '''
    :summary: write_list writes a formatted text to a two column CSV.
    :param srcList: source list to write out
    '''   
    def write_list(self,srcList):

        with codecs.open(self.oConfig,  'w', encoding="utf-8") as out:
    #        sigh. no unicode in csv
    #         wr = _csv.writer(out)
    #         wr.writerow(['workName','outlineText'])
    #         [ wr.writerow([aVal[0],aVal[1]]) for aVal in vals ]
    
            out.write('{0},{1}\n'.format('workName','outlineText'))
            _ =  [ out.write('{0},"{1}"\n'.format(aVal[0],aVal[1].strip())) \
                   for aVal in srcList ]        
        
    
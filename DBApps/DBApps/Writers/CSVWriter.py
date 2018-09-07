"""
Created on Mar 6, 2018

@author: jsk
"""
import codecs
import os
import csv
import pathlib
from DBApps.Writers import listwriter


class CSVWriter(listwriter.ListWriter):
    """
    Writes a list formatted as a CSV file
    """

    '''
    :summary: write_list writes a formatted text to a two column CSV.
    :param srcList: source list to write out
    '''

    def write_list(self, srcList):
        fullFilePath = os.path.expanduser(self.oConfig)
        with codecs.open(fullFilePath, 'w', encoding="utf-8") as out:
            #        sigh. no unicode in csv
            #         wr = _csv.writer(out)
            #         wr.writerow(['workName','outlineText'])
            #         [ wr.writerow([aVal[0],aVal[1]]) for aVal in vals ]

            out.write('{0},{1}\n'.format('workName', 'outlineText'))
            _ = [out.write('{0},"{1}"\n'.format(aVal[0], aVal[1].strip()))
                 for aVal in srcList]

    def write_dict(self, data: dict, columnNames: list):
        """
        Writes slices of a list of dictionary items to a csv.
        Each list element must at least contain a dictionary
        :param data: list of dictionaries
        :param columnNames: list of columns to write (independent of result set)
        :return:
        """
        outPath = pathlib.Path(os.path.expanduser(self.oConfig))
        with outPath.open("w", newline=None) as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            csvwr = csv.DictWriter(fw, columnNames, lineterminator='\n')

            if len(data) > 0:
                csvwr.writeheader()
                for resultRow in data:
                    down_row = {fieldName: resultRow[fieldName] for fieldName in columnNames}
                    csvwr.writerow(down_row)

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
        with codecs.open(self.oConfig, 'w', encoding="utf-8") as out:
            #        sigh. no unicode in csv
            #         wr = _csv.writer(out)
            #         wr.writerow(['workName','outlineText'])
            #         [ wr.writerow([aVal[0],aVal[1]]) for aVal in vals ]

            out.write('{0},{1}\n'.format('workName', 'outlineText'))
            _ = [out.write('{0},"{1}"\n'.format(aVal[0], aVal[1].strip()))
                 for aVal in srcList]

    # TODO: Make a Dictionary CSVWriter class which takes expected column names as arg
    def write_dict(self, data: list, columnNames: list):
        """
        Writes slices of a list of dictionary items to a csv.
        Each list element must at least contain a dictionary
        :param data: list of dictionaries, each entry is a row
        :param columnNames: list of columns to write (independent of result set)
        :return:
        """

        if not self.setup(data):
            return

        with self.osPath.open("w", newline=None) as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            csvwr = csv.DictWriter(fw, columnNames, lineterminator='\n')

            if len(data) > 0:
                csvwr.writeheader()
                for resultRow in data:
                    down_row = {fieldName: resultRow[fieldName] for fieldName in columnNames}
                    csvwr.writerow(down_row)

    # osPath. pathlib representation of file
    _osPath: pathlib.Path

    @property
    def osPath(self):
        return self._osPath

    @osPath.setter
    def osPath(self, value):
        self._osPath = value

    def setup(self, results: list) -> bool:
        """
        Returns true if there is data to write
        :param results: output to write
        :return: true if there is data
        """
        # Anything to do?
        if results is None or len(results) == 0:
            return False
        # Build the output path
        self.MakePathDir(self.osPath)
        return True

    @staticmethod
    def MakePathDir(filePath: pathlib.Path) -> None:
        """
        Creates path to input path if it doesn't exist.
        Resolves any ~ or .. references
        :param filePath: file specification, might contain path
        :type filePath: str
        """
        #
        import os
        fPath = pathlib.Path(os.path.expanduser(str(filePath))).resolve()
        fPath.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

    def PutResultSets(self, results: list, fieldNames: list) -> None:
        """
        Write multiple result sets to file
        :param results: list of list of dicts. represents 0..* result sets
        :param fieldNames: subset of results columns to output
        :return:
        """
        # and write

        if not self.setup(results):
            return

        with self.osPath.open("w", newline='') as fw:
            # Create the CSV writer. NOTE: multiple headers are written to the
            # one output file
            csvwr = csv.DictWriter(fw, fieldNames, lineterminator='\n')
            for resultSet in results:
                if len(resultSet) > 0:
                    csvwr.writeheader()
                    for resultRow in resultSet:
                        down_row = {fieldName: resultRow[fieldName] for fieldName in fieldNames}
                        csvwr.writerow(down_row)

    def __init__(self, fileName: str):
        """
        """
        super().__init__(fileName)
        self.osPath = pathlib.Path(os.path.expanduser(self.oConfig))


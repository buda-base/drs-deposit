"""
    Processor for a CSV file output from WebAdmin.
    Store the required column names and their parameter names here.
    (Parameters are for Routine AddDRS
    The required columns must be present: this class
    returns the vector of their orders
     """
from typing import Dict
import csv


class results:


    def __init__(self, column_dict: dict):
        self.column_dict = column_dict


    def extract_data(self, text_line: str) -> object:
        """
        Creates a parameter dictionary of key:parameter_name, value:parameter_value
        :type text_line: str
        :param text_line:
        :return:
        """
        text_line  = text_line.rstrip('\n')
        line_beads = text_line.split(self.sep)
        if len(line_beads) < len(self.required_columns):
            raise ValueError("not enough data: " + text_line)

        # otherwise, lets go
        # Note we dont care if there are as many values in the lines as there are in the headers -
        # we only want the values at the indexes
        rc = {}
        for k, v in self.column_parameters.items():
            rc[v] = line_beads[self.required_columns[k]]
        return rc

    def csv_to_dict(self, file_name: str) -> Dict[str, str]:
        db_parms = []
        with open(file_name, newline='') as csvfile:
            rdr = csv.DictReader(csvfile)
            for row in rdr:
                # build a list of parms
                {db_parms.append(v, row[k]) for k,v in self.column_dict}
        return db_parms

"""
    Processor for a CSV file output from WebAdmin.
    Store the required column names and their parameter names here.
    (Parameters are for Routine AddDRS
    The required columns must be present: this class
    returns the vector of their orders
     """
from typing import Dict, Any


class results:
    required_columns: Dict[Any, int]
    column_parameters: Dict[Any, object]
    NO_VALUE = -1

    def __init__(self, separator, required_column_list: list):
        self.sep = separator
        # required_column_list must not be empty
        if len(required_column_list) == 0:
            raise ValueError("required column list must have values.")

        self.required_columns = {}
        self.column_parameters = {}

        for s in required_column_list:
            if len(s[0]) == 0:
                raise ValueError("All values in required columns must have length")
            self.required_columns[s[0]] = self.NO_VALUE

            # Save the parameter name into a dictionary
            self.column_parameters[s[0]] = s[1]

    def find_columns(self: object, header_line: object) -> object:
        """
        Populates class variable _required_columns

        Scans the csv input line 0-based column index of each required field
        :type self: object
        :param self:
        :type header_line: string
        :param header_line: header of a CSV report
        :return: throws exception if any _required_columns is not found
        """
        headers = header_line.split(self.sep)
        i_list = 0
        for s in headers:
            if s in self.required_columns:
                self.required_columns[s] = i_list
            i_list += 1

        # Sanity
        missing_headers = []
        for k, v in self.required_columns.items():
            if v == self.NO_VALUE:
                missing_headers.append(k)

        if len(missing_headers) > 0:
            raise ValueError("Required headers missing: " + ' '.join(missing_headers) +  "\n")

    def process_line(self, text_line):
        """
        Creates a parameter dictionary of key:parameter_name, value=parameter_value
        :param text_line:
        :return:
        """

        line_beads = text_line.split(self.sep)
        if len(line_beads) < len(self.required_columns):
            raise ValueError("not enough data: " + text_line)

        # otherwse, lets go
        rc = {}
        for k, v in self.column_parameters:
            rc[v] = text_line[self.required_columns[v]]
        return rc

"""
    Processor for a CSV file output from WebAdmin.
    Encapsulate the required column names here.
    The required columns must be present: this class
    returns the vector of their orders
     """
from typing import Dict, Any


class results:
    required_columns: Dict[Any, int]

    def __init__(self, separator, required_column_list: list):
        self.sep = separator
        # required_column_list must not be empty
        if len(required_column_list) == 0:
            raise ValueError("required column list must have values.")
        self.required_columns = {}
        for s in required_column_list:
            if len(s) == 0:
                raise ValueError("All values in required columns must have length")
            self.required_columns[s] = 0

    def find_columns(self: object, header_line: object) -> object:
        """
        Populates class variable _required_columns

        Scans the csv input line 1-based column index of each required field
        :type self: object
        :param self:
        :type header_line: string
        :param header_line: header of a CSV report
        :return: throws exception if any _required_columns is not found
        """
        headers = header_line.split(self.sep)
        i_list = 0
        for s in headers:
            i_list += 1
            if s in self.required_columns:
                self.required_columns[s] = i_list

        # Sanity
        missing_headers = []
        for k, v in self.required_columns.items():
            if v == 0:
                missing_headers.append(k)

        if len(missing_headers) > 0:
            raise ValueError("Required headers missing: " + ' '.join(missing_headers) +  "\n")

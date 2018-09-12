"""
Read a csv of DRS deposit log entries, extract fields for call to DRS db
sproc 'AddDRS'

"""
import fileinput
import sys
import argparse
from DBApps.Writers.DbWriter import DbWriter
from DBApps.SourceProcessors import WebAdminResults



# The key represents a column in the designated file
required_headers = {
    dict(
        PDS=dict(object_id_num='objectid', object_huldrsadmin_ownerSuppliedName_string='OSN',
                object_urn_string_sort='objectUrn', batch_huldrsadmin_batchDirectoryName_string='DRSDir',
                batch_huldrsadmin_loadStartTime_date='IngestDate', object_fileCount_num='filesCount',
                object_objectSize_num='size'),
        Related=dict(file_id_num='objectid', file_huldrsadmin_ownerSuppliedName_string='OSN',
                     file_huldrsadmin_uri_string_sort='objectUrn', batch_huldrsadmin_batchDirectoryName_string='DRSDir',
                     batch_huldrsadmin_loadStartTime_date='IngestDate', file_premis_size_num='size'))
}
# The value is one of the elements of 'add_drs_params_ordered





add_drs_params_ordered = (
    'IngestDate',
    'objectid',
    'objectUrn',
    'DRSDir',
    'filesCount',
    'size',
    'OSN' # Muy importante!  OSN corresponds to Volume, and is used as the FK from DRS to Volume
)


class GetArgs:
    """
    Holds command line arguments
    """
    pass


def dict_to_add_DRS_param_list(dict_list: dict) -> list:
    """
    Transforms a named dictionary into a list of parameters for DRS.AddDRS
    """

    rc = []
    for a_dict in dict_list:
        a_list = []
        [a_list.append(a_dict[s]) for s in add_drs_params_ordered]
        rc.append(a_list)
    return rc


def DRSUpdate():
    myArgs = GetArgs()

    parse_args(myArgs)
    admin_results = WebAdminResults.WebAdminResults(required_headers)
    param_dict_list = admin_results.csv_to_dict(myArgs.sourceFile)
    # if web_results is None:
    #     web_results = WebAdminResults.WebAdminResults(",", required_headers)
    #     web_results.find_columns(someLine)
    # [outlines.append(web_results.extract_data(someLine)) for someLine in f]

    myArgs.sproc = "AddDRS"
    writer = DbWriter(myArgs)

    param_list = dict_to_add_DRS_param_list(param_dict_list)
    writer.write_list(param_list)


def parse_args(arg_namespace: object) -> object:
    """
    :rtype: object
    :param arg_namespace. class which holds arg values
    """
    _parser = argparse.ArgumentParser \
        (description="Reads  a raw CSV file which holds output of a HUL DRS \
                     WebAdmin search", usage="%(prog)s -d section:configFile sourcefile \
                     where 'section' is a section in a python dbConfig file 'configFile' ")

    _parser.add_argument("sourceFile", help="CSV file containing search WebAdminResults.")
    _parser.add_argument("-d", "--drsDbConfig")
    _parser.add_argument("-r", "--relatedFile", action='store_true',nargs='?')
    _parser.parse_args(namespace=arg_namespace)


if __name__ == '__main__':
    DRSUpdate()

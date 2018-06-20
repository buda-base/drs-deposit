"""
Read a csv of DRS deposit log entries, extract fields for call to DRS db
sproc 'AddDRS'

"""
import fileinput
import sys
import argparse
from DBApps.Writers.DbWriter import DbWriter
from DBApps.SourceProcessors import WebAdminResults

required_headers = {
    'object_id_num' : 'objectid',    
    'object_huldrsadmin_ownerSuppliedName_string' : 'OSN',
    'object_urn_string_sort': 'objectUrn',
    'batch_huldrsadmin_batchDirectoryName_string': 'DRSDir',
    'batch_huldrsadmin_loadStartTime_date': 'IngestDate',
    'object_fileCount_num': 'filesCount',
    'object_objectSize_num': 'size'
    # dontcare "object_huldrsadmin_adminCategory_text_sort",
    # dontcare "object_huldrsadmin_ownerCode_string_sort",
    # dontcare "object_huldrsadmin_billingCode_string",
    # dontcare "object_mets_type_string",
    # dontcare "object_huldrsadmin_role_string_sort",
    # dontcare "object_mets_createDate_date",
    # dontcare "batch_id_num",
    # dontcare "batch_huldrsadmin_batchName_string",
    # dontcare "object_huldrsadmin_adminFlagType_string_sort",
    # dontcare "object_huldrsadmin_accessFlag_string",
    # dontcare "object_mods_title_text_sort",
    # dontcare "object_huldrsadmin_producer_string_sort"
}
    
add_drs_params_ordered = (
'IngestDate',
'objectid',
'objectUrn',
'DRSDir',
'filesCount',
'size',
'OSN'
)

class getArgs:
    """
    Holds command line arguments
    """
    pass

def dict_to_add_DRS_param_list(dict_list: dict) -> list :
    """
    Transforms a named dictionary into a list of parameters for DRS.AddDRS
    """

    rc=[]
    for a_dict in dict_list:
        a_list = []
        [a_list.append(a_dict[s]) for s in add_drs_params_ordered]
        rc.append(a_list)
    return rc
def DRSUpdate(args):
    web_results: WebAdminResults
    myArgs = getArgs()

    parse_args(myArgs)
    admin_results = WebAdminResults.results(required_headers)
    param_dict_list = admin_results.csv_to_dict(myArgs.sourceFile)
        # if web_results is None:
        #     web_results = WebAdminResults.results(",", required_headers)
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
    _parser = argparse.ArgumentParser\
        (description="Reads  a raw CSV file which holds output of a HUL DRS \
                     WebAdmin search", usage="%(prog)s -d section:configFile sourcefile \
                     where 'section' is a section in a python config file 'configFile' ")

    _parser.add_argument("sourceFile", help="CSV file containing search results.")
    _parser.add_argument("-d", "--drsDbConfig")
    _parser.parse_args(namespace=arg_namespace)


if __name__ == '__main__':
    DRSUpdate(sys.argv[1:])

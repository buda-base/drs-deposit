"""
    Processor for a CSV file output from WebAdmin.
    Encapsulate the required column names here.
    The required columns must be present: this class
    returns the vector of their orders
     """
_requiredColumns = {
    {"object_id_num": 0},   #objectId
    {"object_huldrsadmin_ownerSuppliedName_string": 0}, # OSN
    {"object_urn_string_sort": 0},  #objectUrn
    {"batch_huldrsadmin_batchDirectoryName_string": 0}, # batchDir
    {"batch_huldrsadmin_loadStartTime_date": 0}, # IngestDate
    {"object_fileCount_num": 0},  # filesCount
    {"object_objectSize_num": 0}  # size
    # dontcare {"batch_huldrsadmin_batchName_string": 0},
    # dontcare {"batch_id_num": 0},
    # dontcare {"object_huldrsadmin_adminFlagType_string_sort": 0},
    # dontcare {"object_huldrsadmin_accessFlag_string": 0},
    # dontcare {"object_mods_title_text_sort": 0},
    # dontcare {"object_huldrsadmin_producer_string_sort": 0},
    # dontcare {"object_huldrsadmin_adminCategory_text_sort": 0},
    # dontcare         {"object_huldrsadmin_ownerCode_string_sort": 0},
    # dontcare {"object_huldrsadmin_billingCode_string": 0},
    # dontcare {"object_mets_type_string": 0},
    # dontcare {"object_huldrsadmin_role_string_sort": 0},
    # dontcare {"object_mets_createDate_date": 0},

}
class WebAdminResults:

    def __init__(self):
        pass

"""
Builds the csv inventory to submit volumes of a work
"""

from __future__ import annotations

import dataclasses

import requests
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
from dataclasses import dataclass

# This is the union of all the metadata we're going to provide. Any
# given row in the submittal file will contain some of these values.
# csv.Dictwriter provides sparse mapping (i.e. a row can be a dict with only
# a subset of columns
SUBMITTAL_COLUMNS = [
    "FullFolderOrFilePath",
    "ObjResType",
    "ProcArchMode",
    "D3OSN",
    "D3Label",
    "FilePurpose",
    "FileRole",
    "FileAccFlag",
    "MIXTileHt",
    "MIXTileWidth",
    "MODSTitle",
    "MODSName",
    "MODSPublisher",
    "MODSPlace",
    "MODSEdition",
    "MODSAbstract",
    "MODSSubject",
    "MODSGenre",
    "MODSIdentifier",
    "MODSRelatedItem",
    "MODSLanguage",
    "D3SubName"
]

MARC_NAMESPACE = "http://www.loc.gov/MARC21/slim"
MARC_NAMESPACES = {"marc": MARC_NAMESPACE}
BUDA_MARC_URL = "https://purl.bdrc.io/resource/{w}.xml"


def _extract_marc_text(root: ET.ElementTree, tag: str, code: str | None) -> str:

    xpath = f".//marc:datafield[@tag='{tag}']"
    xpath += f"/marc:subfield[@code='{code}']" if code else ""
    nodes = root.findall(xpath, MARC_NAMESPACES)

    # return the first found
    # Don't bother testing for strip - return empty string is fine
    for node in nodes:
        if node.text:
            return node.text.strip()
    return ""


def _get_metadata_value(instance: DRS3_Base, key: str) -> Any:
    return "silence, PyLance"

@dataclass
class DRS3_Base:
    """
    Commmon methods for all the DRS3 objects
    """

    path: Path
    # Not a Image_Meta or DRTS3_Base
    parent: ObjectBase | None

    #----------- Common  accessors -----------------
    @staticmethod
    def get_path(instance: DRS3_Base) -> str:
        parent_path = f"/{instance.parent.path.name}" if instance.parent else ""
        return f"{parent_path}/{instance.path.name}" 

    @staticmethod
    def get_osn(instance: DRS3_Base) -> Any:
        return instance.path.name

    #-----    DRS3 Object accessors.  -----------
    @staticmethod
    def get_marc_value(instance: DRS3_Base, marc_spec: str) -> Any:
        raise NotImplementedError("get_marc_value must be implemented by subclasses")

    @staticmethod
    def get_obj_res_type(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_obj_res_type must be implemented by subclasses")

    
    @staticmethod
    def get_d3_sub_name(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_d3_sub_name must be implemented by subclasses")

    #--------       DRS3 File accessors. -------------
    @staticmethod
    def get_file_purpose(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_file_purpose must be implemented by subclasses")

    @staticmethod
    def get_file_role(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_file_role must be implemented by subclasses")
    
    @staticmethod
    def get_file_acc_flag(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_file_acc_flag must be implemented by subclasses")

    @staticmethod
    def get_mix_tile_height(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_mix_tile_height must be implemented by subclasses")

    @staticmethod
    def get_mix_tile_width(instance: DRS3_Base) -> Any:
        raise NotImplementedError("get_mix_tile_width must be implemented by subclasses ")


@dataclass
class ObjectBase(DRS3_Base):
    """
    Base class for all DRS3 objects of Object type
    """

    @staticmethod
    def get_obj_res_type(instance: ObjectBase) -> Any:
        return _get_metadata_value(instance, "ObjResType")


@dataclass
class Work_Meta(ObjectBase):

    _marc_root: ET.ElementTree

    @staticmethod   
    def get_path(instance: Work_Meta) -> str:
        """
        Is simply the work name - the terminal node of the path, prefixed with '/'
        """
        return f"/{instance.path.name}"

    @staticmethod
    def get_d3_sub_name(instance: DRS3_Base) -> Any:
        return _get_metadata_value(instance, "D3SubName")

    @staticmethod
    def get_osn(instance: Work_Meta) -> Any:
        raise NotImplementedError("get_os must be implemented by subclasses")

    @staticmethod
    def get_marc_field(instance: Work_Meta, tag: str, code : str | None = None) -> Any:
        return _extract_marc_text(instance._marc_root, tag, code)


    def populate_metadata(self) -> dict[str, str]:
        """
        Create a list of dictionaries that represents the work's metadata.
        """
        def get_marc_metadata( work_name: str) -> ET.Element:
            """
            Call purl.bdrc.io to retrieve the MARC XML metadata for the given work name, and 
            return the xml element tree
            """
    
            response = requests.get(BUDA_MARC_URL.format(w=work_name))
            response.raise_for_status()
            return ET.fromstring(response.content)

        if self._marc_root is None:
            self._marc_root = get_marc_metadata(self.path.name)

        metadata = {}
        for key, value in WORK_METADATA_TEMPLATE.items():
            if isinstance(value, tuple) and len(value) > 1 and callable(value[0]):
                metadata[key] = value[0](self, *value[1:])
            elif callable(value):
                metadata[key] = value(self)
            else:
                metadata[key] = value
        return metadata
   

    #        ----    Instance Methods --------
    def discover_volumes(self) -> None:
        raise NotImplementedError

@dataclass
class Volume_Meta(ObjectBase):
    image_files: list[Image_Meta] = dataclasses.field(default_factory=list)

@dataclass
class Image_Meta(DRS3_Base):
    path: Path
    parent: Volume_Meta

    @staticmethod
    def get_path(instance: Image_Meta) -> str:
        return f"{instance.parent.get_path(instance.parent)}/{instance.path.name}"

    @staticmethod
    def get_file_role(instance: Image_Meta) -> Any:
        return _get_metadata_value(instance, "FileRole")

    @staticmethod
    def get_file_acc_flag(instance: Image_Meta) -> Any:
        return _get_metadata_value(instance, "FileAccFlag")

    @staticmethod
    def get_mix_tile_height(instance: Image_Meta) -> Any:
        return _get_metadata_value(instance, "MIXTileHt")

    @staticmethod
    def get_mix_tile_width(instance: Image_Meta) -> Any:
        return _get_metadata_value(instance, "MIXTileWidth")

    def populate_metadata(self) -> None:
        raise NotImplementedError


WORK_METADATA_TEMPLATE = {
    "FullFolderOrFilePath" : Work_Meta.get_path,
    "D3OSN": Work_Meta.get_osn,
#    "D3Label": Work_Meta.get_d3_label,
    "ObjResType": "Page-turned list",
    "MODSTitle": (Work_Meta.get_marc_field, "245" ,"a"),
    "MODSName": (Work_Meta.get_marc_field, "024" , "a"),
    "MODSPublisher": (Work_Meta.get_marc_field, "264" , "b"),
    "MODSPlace": (Work_Meta.get_marc_field, "264" , "a"),
    "MODSEdition": (Work_Meta.get_marc_field, "250" , "a"),
    # Not used
    # "MODSAbstract": [_metadata_populator(), None, None],
    "MODSSubject": (Work_Meta.get_marc_field, "520" , "a"),
    "MODSGenre": (Work_Meta.get_marc_field, "655" , "a"),
    # Not used
    # "MODSIdentifier": 
    # "MODSRelatedItem": 
    "MODSLanguage": (Work_Meta.get_marc_field, "546" , "a"),
    "D3SubName": Work_Meta.get_d3_sub_name,
}

VOLUME_METADATA_TEMPLATE = {
    "FullFolderOrFilePath" : Volume_Meta.get_path,
    "D3OSN": Volume_Meta.get_osn,
    "ObjResType": "Page-turned",
}

FILE_METADATA_TEMPLATE = {
    "FullFolderOrFilePath" : Image_Meta.get_path,
    "D3OSN": Image_Meta.get_osn,
    "FilePurpose":  "DATA",
    "FileRole": "PAGE_IMAGE",
    # Not used - take the system provided default of 'R'
    # "FileAccFlag": None,
    "MIXTileHt": None,
    "MIXTileWidth": None,

}


def populate_metadata(work_path: Path) -> list[dict[str, Any]]:
    """
    Build the work's metadata into a list of dictionairies. Output:
    [
        work_metadata_dict,
        *[volume.populate_metadata() for volume in work.discover_volumes()],
    ]
    where each volume.populate_metadata() returns:
    [ 
        volume_metadata_dict,
        [*file.populate_metadata() for file in volume.discover_files()]
    ]
    Each dictionary may have different keys, but each key will be a member of SUBMITTAL_COLUMNS.keys()
    """
    work_metadata = Work_Meta(path=work_path)
    return [ work_metadata.populate_metadata(), *[volume.populate_metadata() for volume in  work_metadata.discover_volumes()]]


def metadata_to_csv(metadata_list: list[dict[str, Any]], csv_path: Path) -> None:
    """
    Write a list of metadata dictionaries to a CSV file.

    Each dictionary in the list represents a set of metadata fields for a work, volume, or file.
    The keys of the dictionaries should correspond to the columns in the CSV.

    Args:
        metadata_list: A list of dictionaries containing metadata.
        csv_path: The path to the CSV file to write.
    """
    import csv

    if not metadata_list:
        return

    # Create a dictionary with all the keys in SUBMITTAL_COLUMNS (without touching SUBMITTAL_COLUMNS)
    all_keys = {key for metadata in metadata_list for key in metadata.keys()}
    all_rows: list[dict[str, Any]] = []
    
    # for each dictionary in metadata_list, create a new dictionary with all keys from all_keys
    # and fill in the values from the original dictionary 
    # (dict.get(key) returns  None if the key is missing)
    #
    # Achtung: the csv module will handle the escaping of values containing quotes or strings
    for metadata in metadata_list:
        row = {key: metadata.get(key) for key in all_keys}
        all_rows.append(row)

    with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, 
                                fieldnames=all_keys,
                                extrasaction="ignore", # Copilot AI suggestion
                                restval="" )           # Copilot AI suggestion
        writer.writeheader()
        writer.writerows(all_rows)

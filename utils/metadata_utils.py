"""
Builds the csv inventory to submit volumes of a work
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import requests
from PIL import Image, UnidentifiedImageError
from mypy.semanal import names_modified_by_assignment

# This is the union of all the metadata we're going to provide. Any
# given row in the submittal file will contain some of these values.
# csv.Dictwriter provides sparse mapping (i.e. a row can be a dict with only
# a subset of columns
SUBMITTAL_COLUMNS = [
    "FullFolderOrFilePath",
    "ObjResType",
#    "ProcArchMode", Take default
    "D3OSN",
    "D3Label",
    "FilePurpose",
    "FileRole",
# Take default    "FileAccFlag",
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
    "MODSLanguage"
#    "D3SubName" Unknown what to fill in
]

MARC_NAMESPACE = "http://www.loc.gov/MARC21/slim"
MARC_NAMESPACES = {"marc": MARC_NAMESPACE}
BUDA_MARC_URL = "https://purl.bdrc.io/resource/{w}.mrcx"
IMAGE_GROUP_HOME="drs"

def fetch_marc_metadata( work_name: str) -> ET.ElementTree:
    """
    Call purl.bdrc.io to retrieve the MARC XML metadata for the given work name, and 
    return the xml element tree
    """

    response = requests.get(BUDA_MARC_URL.format(w=work_name))
    response.raise_for_status()
    return ET.ElementTree(ET.fromstring(response.content))


def _extract_marc_text(root: ET.ElementTree , tag: str, code: str | None) -> str:

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


def _read_image_dimensions(path: Path) -> tuple[int, int] | None:
    """Return image (height, width) when Pillow can identify the file, else None."""
    try:
        with Image.open(path) as image:
            return image.height, image.width
    except (UnidentifiedImageError, OSError):
        return None


@dataclass
class DRS3_Base:
    """
    Commmon methods for all the DRS3 objects
    """

    path: Path
    # Not a Image_Meta or DRTS3_Base
    parent: ObjectBase | None = None

    #----------- Common  accessors -----------------
    @staticmethod
    def get_path(instance: DRS3_Base) -> str:
        """
        Simply the terminal node, prefixed by the parent's terminal node if it exists.
        """
        parent_path = f"/{instance.parent.path.name}" if instance.parent else ""
        return f"{parent_path}/{instance.path.name}" 

    @staticmethod
    def get_osn(instance: DRS3_Base) -> Any:
        return instance.path.name

    def _populate_from_template(self, template: dict[str, Any]) -> dict[str, Any]:
        """
        Populate one metadata row for this instance from a template.
        """

        metadata: dict[str, Any] = {}
        for key, value in template.items():
            if isinstance(value, tuple) and len(value) > 1 and callable(value[0]):
                metadata[key] = value[0](self, *value[1:])
            elif callable(value):
                metadata[key] = value(self)
            else:
                metadata[key] = value
        return metadata

    def get_metadata_template(self) -> dict[str, Any]:
        raise NotImplementedError("get_metadata_template must be implemented by subclasses")

    def discover_children(self) -> Sequence[DRS3_Base]:
        return []

    def populate_metadata(self) -> list[dict[str, Any]]:
        """Recursively populate metadata rows for this instance and all children."""

        rows: list[dict[str, Any]] = [self._populate_from_template(self.get_metadata_template())]
        for child in self.discover_children():
            rows.extend(child.populate_metadata())
        return rows

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
    volumes: list[Volume_Meta] = dataclasses.field(default_factory=list)
    _marc_root: ET.ElementTree = field(init=False, repr=False, compare=False)


    def set_marc_root(self, root: ET.ElementTree) -> None:
        self._marc_root = root

 
# ..

    @staticmethod
    def get_d3_sub_name(instance: DRS3_Base) -> Any:
        return _get_metadata_value(instance, "D3SubName")

    @staticmethod
    def get_osn(instance: Work_Meta) -> Any:
        return instance.path.name

    def get_metadata_template(self) -> dict[str, Any]:
        return WORK_METADATA_TEMPLATE

    @staticmethod
    def get_marc_field(instance: Work_Meta, tag: str, code : str | None = None) -> Any:
        """
        Retrieve the value of a MARC field from the work's MARC metadata. Load it
        as needed.
        """
        if not hasattr(instance, "_marc_root"):
            instance.set_marc_root(fetch_marc_metadata(instance.path.name))
        return _extract_marc_text(instance._marc_root, tag, code)


    #        ----    Instance Methods --------
    def discover_volumes(self) -> list[Volume_Meta]:
        """
        The volumes in a work are the names of the directories immediately under
        the directory IMAGE_GROUP_HOME under the work's directory in the file system.
        """
        image_group_path = self.path / IMAGE_GROUP_HOME
        if not image_group_path.exists() or not image_group_path.is_dir():
            raise ValueError(f"Home of Volumes does not exist or is not a directory: {image_group_path}")

        self.volumes = [
            Volume_Meta(path=entry, parent=self)
            for entry in sorted(image_group_path.iterdir())
            if entry.is_dir()
        ]
        return self.volumes

    def discover_children(self) -> Sequence[DRS3_Base]:
        return self.discover_volumes()

@dataclass
class Volume_Meta(ObjectBase):
    image_files: list[Image_Meta] = dataclasses.field(default_factory=list)

    def get_metadata_template(self) -> dict[str, Any]:
        return VOLUME_METADATA_TEMPLATE

    def discover_images(self) -> list[Image_Meta]:
        """
        The images in a volume are the names of the files immediately under
        the volume's directory in the file system.
        """

        if not self.path.exists() or not self.path.is_dir():
            raise ValueError(f"Images path does not exist or is not a directory: {self.path}")

        self.image_files = []
        for entry in sorted(self.path.iterdir()):
            if not entry.is_file():
                continue
            dimensions = _read_image_dimensions(entry)
            if dimensions is None:
                continue
            height, width = dimensions
            self.image_files.append(
                Image_Meta(path=entry, parent=self, image_height=height, image_width=width)
            )
        return self.image_files

    def discover_children(self) -> Sequence[DRS3_Base]:
        return self.discover_images()

@dataclass
class Image_Meta(DRS3_Base):
    image_height: int = 0
    image_width: int = 0

    def get_metadata_template(self) -> dict[str, Any]:
        return FILE_METADATA_TEMPLATE

    @staticmethod
    def get_path(instance: Image_Meta) -> str:
        if instance.parent is None:
            return f"/{instance.path.name}"
        return f"{DRS3_Base.get_path(instance.parent)}/{instance.path.name}"

    @staticmethod
    def get_file_role(instance: Image_Meta) -> Any:
        return _get_metadata_value(instance, "FileRole")

    @staticmethod
    def get_file_acc_flag(instance: Image_Meta) -> Any:
        return _get_metadata_value(instance, "FileAccFlag")

    @staticmethod
    def get_height(instance: Image_Meta) -> Any:
        return instance.image_height

    @staticmethod
    def get_width(instance: Image_Meta) -> Any:
        return instance.image_width

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
    "MODSLanguage": (Work_Meta.get_marc_field, "546" , "a")
#    "D3SubName": Work_Meta.get_d3_sub_name,
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
    "MIXTileHt": Image_Meta.get_height,
    "MIXTileWidth": Image_Meta.get_width,

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
    return work_metadata.populate_metadata()


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

    with open(csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, 
                                fieldnames=SUBMITTAL_COLUMNS,
                                extrasaction="ignore", # Copilot AI suggestion
                                restval="" )           # Copilot AI suggestion
        writer.writeheader()

        # NB that [md_entry.keys() for md_entry in metadata_list] is a subset of
        # the columns in SUBMITTAL_COLUMNS. DictWriters handle the sparsity
        writer.writerows(metadata_list)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python utils/metadata_utils.py <work_path> <csv_path>")
        sys.exit(1)
    work_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])
    metadata_list = populate_metadata(work_path)
    metadata_to_csv(metadata_list, csv_path)
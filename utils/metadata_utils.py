"""
Builds the csv inventory to submit volumes of a work
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

SUBMITTAL_COLUMNS = {
    "FullFolderOrFilePath": None,
    "ObjResType": None,
    "ProcArchMode": None,
    "D3OSN": None,
    "D3Label": None,
    "FilePurpose": None,
    "FileRole": None,
    "FileAccFlag": None,
    "MIXTileHt": None,
    "MIXTileWidth": None,
    "MODSTitle": None,
    "MODSName": None,
    "MODSPublisher": None,
    "MODSPlace": None,
    "MODSEdition": None,
    "MODSAbstract": None,
    "MODSSubject": None,
    "MODSGenre": None,
    "MODSIdentifier": None,
    "MODSRelatedItem": None,
    "MODSLanguage": None,
    "D3SubName": None,
}

type Getter = Callable[[Any], Any]
type RowMutator = Callable[[Any, dict[str, Any]], None]

MARC_NAMESPACE = "http://www.loc.gov/MARC21/slim"
MARC_NAMESPACES = {"marc": MARC_NAMESPACE}
MARC_SPEC_PATTERN = re.compile(r"^Marc\.tag\.(\d{1,3})\.code\.([A-Za-z0-9])$")


def _get_metadata_value(instance: Any, column_name: str) -> Any:
    return instance.metadata.get(column_name)


def _set_row_value(row: dict[str, Any], column_name: str, value: Any) -> None:
    row[column_name] = value


def _constant_mutator(column_name: str, value: Any) -> RowMutator:
    def _mutate(_instance: Any, row: dict[str, Any]) -> None:
        _set_row_value(row, column_name, value)

    return _mutate


def _getter_mutator(column_name: str, getter: Getter) -> RowMutator:
    def _mutate(instance: Any, row: dict[str, Any]) -> None:
        _set_row_value(row, column_name, getter(instance))

    return _mutate


def _metadata_mutator(column_name: str, metadata_key: str) -> RowMutator:
    def _mutate(instance: Any, row: dict[str, Any]) -> None:
        _set_row_value(row, column_name, _get_metadata_value(instance, metadata_key))

    return _mutate


def _marc_mutator(column_name: str, marc_spec: str) -> RowMutator:
    def _mutate(instance: Any, row: dict[str, Any]) -> None:
        if not hasattr(instance, "get_marc_value"):
            _set_row_value(row, column_name, None)
            return
        _set_row_value(row, column_name, instance.get_marc_value(marc_spec))

    return _mutate


def _parse_marc_spec(marc_spec: str) -> tuple[str, str]:
    match = MARC_SPEC_PATTERN.match(marc_spec)
    if match is None:
        msg = f"Invalid MARC spec format: {marc_spec!r}"
        raise ValueError(msg)
    tag = match.group(1).zfill(3)
    code = match.group(2)
    return tag, code


def _extract_marc_text(root: ET.Element, marc_spec: str) -> str | None:
    tag, code = _parse_marc_spec(marc_spec)
    xpath = f".//marc:datafield[@tag='{tag}']/marc:subfield[@code='{code}']"
    nodes = root.findall(xpath, MARC_NAMESPACES)
    for node in nodes:
        if node.text and node.text.strip():
            return node.text.strip()
    return None


@dataclasses.dataclass
class ImageFileForDRS3Metadata:
    path: Path
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_path(instance: ImageFileForDRS3Metadata) -> str:
        return str(instance.path)

    @staticmethod
    def get_obj_res_type(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "ObjResType")

    @staticmethod
    def get_file_purpose(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "FilePurpose")

    @staticmethod
    def get_file_role(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "FileRole")

    @staticmethod
    def get_file_acc_flag(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "FileAccFlag")

    @staticmethod
    def get_mix_tile_height(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "MIXTileHt")

    @staticmethod
    def get_mix_tile_width(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "MIXTileWidth")

    @staticmethod
    def get_d3_sub_name(instance: ImageFileForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3SubName")

    def to_submittal_dict(self) -> dict[str, Any]:
        return build_submittal_dict(self)

    def get_marc_value(self, marc_spec: str) -> Any:
        raise NotImplementedError

    def populate_metadata(self) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class VolumeForDRS3Metadata:
    path: Path
    image_files: list[ImageFileForDRS3Metadata] = dataclasses.field(default_factory=list)
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    @staticmethod
    def get_path(instance: VolumeForDRS3Metadata) -> str:
        return str(instance.path)

    @staticmethod
    def get_obj_res_type(instance: VolumeForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "ObjResType")

    @staticmethod
    def get_proc_arch_mode(instance: VolumeForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "ProcArchMode")

    @staticmethod
    def get_osn(instance: VolumeForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3OSN")

    @staticmethod
    def get_d3_label(instance: VolumeForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3Label")

    @staticmethod
    def get_d3_sub_name(instance: VolumeForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3SubName")

    def to_submittal_dict(self) -> dict[str, Any]:
        return build_submittal_dict(self)

    def get_marc_value(self, marc_spec: str) -> Any:
        raise NotImplementedError

    def discover_image_files(self) -> None:
        raise NotImplementedError

    def populate_metadata(self) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class WorkForDRS3Metadata:
    path: Path
    volumes: list[VolumeForDRS3Metadata] = dataclasses.field(default_factory=list)
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)
    marc_xml_path: Path | None = None
    _marc_root: ET.Element | None = dataclasses.field(default=None, init=False, repr=False)

    @staticmethod
    def get_path(instance: WorkForDRS3Metadata) -> str:
        return str(instance.path)

    @staticmethod
    def get_obj_res_type(instance: WorkForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "ObjResType")

    @staticmethod
    def get_proc_arch_mode(instance: WorkForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "ProcArchMode")

    @staticmethod
    def get_osn(instance: WorkForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3OSN")

    @staticmethod
    def get_d3_label(instance: WorkForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3Label")

    @staticmethod
    def get_d3_sub_name(instance: WorkForDRS3Metadata) -> Any:
        return _get_metadata_value(instance, "D3SubName")

    def to_submittal_dict(self) -> dict[str, Any]:
        return build_submittal_dict(self)

    def get_marc_value(self, marc_spec: str) -> Any:
        if marc_spec in self.metadata:
            return self.metadata[marc_spec]

        if self._marc_root is None:
            xml_path = self.marc_xml_path
            if xml_path is None:
                meta_xml_path = self.metadata.get("MarcXmlPath")
                if isinstance(meta_xml_path, str) and meta_xml_path.strip():
                    xml_path = Path(meta_xml_path)
            if xml_path is None:
                return None
            tree = ET.parse(xml_path)
            self._marc_root = tree.getroot()

        return _extract_marc_text(self._marc_root, marc_spec)

    def discover_volumes(self) -> None:
        raise NotImplementedError

    def populate_metadata(self) -> None:
        raise NotImplementedError


_WORK_INDEX = 0
_VOLUME_INDEX = 1
_IMAGE_INDEX = 2


# Column -> [work_populator, volume_populator, image_populator]
COLUMN_POPULATORS: dict[str, list[RowMutator | None]] = {
    "FullFolderOrFilePath": [
        _getter_mutator("FullFolderOrFilePath", WorkForDRS3Metadata.get_path),
        _getter_mutator("FullFolderOrFilePath", VolumeForDRS3Metadata.get_path),
        _getter_mutator("FullFolderOrFilePath", ImageFileForDRS3Metadata.get_path),
    ],
    "ObjResType": [
        _constant_mutator("ObjResType", "Page-turned list"),
        _constant_mutator("ObjResType", "Page-turned"),
        None,
    ],
    # Not used - DRS provides a default - will change to AutoClean
    # When DRS releases it
    # "ProcArchMode": [
    #     WorkForDRS3Metadata.get_proc_arch_mode,     # You
    #     VolumeForDRS3Metadata.get_proc_arch_mode,   # get the
    #     None,                                       # idea
    # ],
    "D3OSN": [
        _getter_mutator("D3OSN", WorkForDRS3Metadata.get_osn),
        _getter_mutator("D3OSN", VolumeForDRS3Metadata.get_osn),
        None,
    ],
    "D3Label": [
        _getter_mutator("D3Label", WorkForDRS3Metadata.get_d3_label),
        _getter_mutator("D3Label", VolumeForDRS3Metadata.get_d3_label),
        None,
    ],
    "FilePurpose": [None, None, _constant_mutator("FilePurpose", "DATA")],
    "FileRole": [None, None, _constant_mutator("FileRole", "PAGE_IMAGE")],
    # DRS provides default - R Restricted to known internal users
    # "FileAccFlag": [None, None, ImageFileForDRS3Metadata.get_file_acc_flag],
    "MIXTileHt": [None, None, _getter_mutator("MIXTileHt", ImageFileForDRS3Metadata.get_mix_tile_height)],
    "MIXTileWidth": [None, None, _getter_mutator("MIXTileWidth", ImageFileForDRS3Metadata.get_mix_tile_width)],
    "MODSTitle": [_marc_mutator("MODSTitle", "Marc.tag.245.code.a"), None, None],
    "MODSName": [_marc_mutator("MODSName", "Marc.tag.024.code.a"), None, None],
    "MODSPublisher": [_marc_mutator("MODSPublisher", "Marc.tag.264.code.b"), None, None],
    "MODSPlace": [_marc_mutator("MODSPlace", "Marc.tag.264.code.a"), None, None],
    "MODSEdition": [_marc_mutator("MODSEdition", "Marc.tag.250.code.a"), None, None],
    # Not used
    # "MODSAbstract": [_metadata_populator(), None, None],
    "MODSSubject": [_marc_mutator("MODSSubject", "Marc.tag.520.code.a"), None, None],
    "MODSGenre": [_marc_mutator("MODSGenre", "Marc.tag.655.code.a"), None, None],
    # Not used
    # "MODSIdentifier": [_metadata_populator("MODSIdentifier"), None, None],
    # "MODSRelatedItem": [_metadata_populator("MODSRelatedItem"), None, None],
    "MODSLanguage": [_marc_mutator("MODSLanguage", "Marc.tag.546.code.a"), None, None],
    "D3SubName": [
        _getter_mutator("D3SubName", WorkForDRS3Metadata.get_d3_sub_name),
        None,
        None,
    ],
}


def _instance_index(instance: Any) -> int:
    if isinstance(instance, WorkForDRS3Metadata):
        return _WORK_INDEX
    if isinstance(instance, VolumeForDRS3Metadata):
        return _VOLUME_INDEX
    if isinstance(instance, ImageFileForDRS3Metadata):
        return _IMAGE_INDEX
    msg = f"Unsupported metadata type: {type(instance)!r}"
    raise TypeError(msg)


def build_submittal_dict(instance: Any) -> dict[str, Any]:
    index = _instance_index(instance)
    row: dict[str, Any] = {column_name: None for column_name in SUBMITTAL_COLUMNS}

    for column_name in SUBMITTAL_COLUMNS:
        operations = COLUMN_POPULATORS.get(column_name, [None, None, None])
        operation = operations[index]
        if operation is not None:
            operation(instance, row)

    return row


def build_submittal_rows_for_work(work: WorkForDRS3Metadata) -> list[dict[str, Any]]:
    """Return submittal rows in this order: work, volumes, then image files."""

    rows: list[dict[str, Any]] = [work.to_submittal_dict()]

    for volume in work.volumes:
        rows.append(volume.to_submittal_dict())
        rows.extend(image_file.to_submittal_dict() for image_file in volume.image_files)

    return rows


def build_example_work_tree() -> WorkForDRS3Metadata:
    """Build a minimal sample object graph for testing row emission."""

    image_1 = ImageFileForDRS3Metadata(
        path=Path("/W1/work/v001/images/0001.tif"),
        metadata={
            "ObjResType": "Image",
            "FilePurpose": "Data",
            "FileRole": "PAGE_IMAGE",
            "FileAccFlag": "Public",
            "MIXTileHt": 4000,
            "MIXTileWidth": 3000,
            "D3SubName": "W1_v001_0001",
        },
    )

    volume_1 = VolumeForDRS3Metadata(
        path=Path("/W1/work/v001"),
        image_files=[image_1],
        metadata={
            "ObjResType": "Volume",
            "ProcArchMode": "Manual",
            "D3OSN": "W1",
            "D3Label": "Volume 1",
            "D3SubName": "W1_v001",
        },
    )

    work = WorkForDRS3Metadata(
        path=Path("/W1/work"),
        volumes=[volume_1],
        metadata={
            "ObjResType": "Page-turned list",
            "ProcArchMode": "Manual",
            "D3OSN": "W1",
            "D3Label": "Work W1",
            "MODSTitle": "Example Work",
            "MODSName": "Example Creator",
            "MODSPublisher": "Example Publisher",
            "MODSPlace": "Lhasa",
            "MODSEdition": "First edition",
            "MODSSubject": "Buddhist literature",
            "MODSGenre": "Collected works",
            "MODSLanguage": "Tibetan",
            "D3SubName": "W1_2026-08-25",
        },
    )

    return work
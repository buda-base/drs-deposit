from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Final
from xml.etree import ElementTree as ET

MARC_NAMESPACE: Final[str] = "http://www.loc.gov/MARC21/slim"
NAMESPACES: Final[dict[str, str]] = {"marc": MARC_NAMESPACE}


def _default_map_csv_path() -> Path:
	return Path(__file__).resolve().parents[1] / "docs" / "DRS-MARC-MODS-map.csv"


def _default_xml_path() -> Path:
	return Path(__file__).resolve().parents[1] / "docs" / "sample-marc.xml"


def _first_text_for_row(root: ET.Element, datafield_tag: str, subfield_code: str) -> str | None:
	normalized_tag = datafield_tag.zfill(3) if datafield_tag.isdigit() else datafield_tag
	xpath = (
		f".//marc:datafield[@tag='{normalized_tag}']"
		f"/marc:subfield[@code='{subfield_code}']"
	)
	elements = root.findall(xpath, NAMESPACES)
	for element in elements:
		if element.text and element.text.strip():
			return element.text.strip()
	return None


def build_drs_eic_value_map(
	map_csv_path: str | Path | None = None,
	xml_path: str | Path | None = None,
) -> dict[str, str]:
	"""Build a DRS-EIC keyed map from the MARC mapping CSV and XML source.

	Only rows with non-empty DRS-EIC, MdataFtag, and MsubCode are included.
	Each included key maps to the first matching MARC subfield text value.
	"""

	resolved_map_csv_path = Path(map_csv_path) if map_csv_path else _default_map_csv_path()
	resolved_xml_path = Path(xml_path) if xml_path else _default_xml_path()

	tree = ET.parse(resolved_xml_path)
	root = tree.getroot()

	result: dict[str, str] = {}
	with resolved_map_csv_path.open("r", encoding="utf-8", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			key = (row.get("DRS-EIC") or "").strip()
			datafield_tag = (row.get("MdataFtag") or "").strip()
			subfield_code = (row.get("MsubCode") or "").strip()

			if not key or not datafield_tag or not subfield_code:
				continue

			value = _first_text_for_row(root, datafield_tag, subfield_code)
			if value is not None:
				result[key] = value

	return result


def _build_arg_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="Build a DRS-EIC keyed dictionary from mapping CSV and MARC XML.",
	)
	parser.add_argument(
		"--map-csv",
		default=str(_default_map_csv_path()),
		help="Path to DRS-MARC-MODS-map.csv",
	)
	parser.add_argument(
		"--xml",
		default=str(_default_xml_path()),
		help="Path to source MARC XML file",
	)
	parser.add_argument(
		"--output",
		default=None,
		help="Optional JSON output file path; defaults to stdout",
	)
	return parser


def main() -> None:
	parser = _build_arg_parser()
	args = parser.parse_args()
	output_map = build_drs_eic_value_map(args.map_csv, args.xml)

	if args.output:
		output_path = Path(args.output)
		output_path.write_text(json.dumps(output_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
		return

	print(json.dumps(output_map, indent=2, ensure_ascii=False))


if __name__ == "__main__":
	main()

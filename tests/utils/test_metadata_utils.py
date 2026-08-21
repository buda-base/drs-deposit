from pathlib import Path

from utils.metadata_utils import build_drs_eic_value_map


def test_build_drs_eic_value_map_uses_defaults() -> None:
    output = build_drs_eic_value_map()

    assert output["D3OSN"] == "W1AC29"
    assert output["MODSPublisher"].startswith("Ser gtsug")
    assert "ObjPurpose" not in output


def test_build_drs_eic_value_map_with_explicit_paths() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    map_csv = repo_root / "docs" / "DRS-MARC-MODS-map.csv"
    xml_path = repo_root / "docs" / "sample-marc.xml"

    output = build_drs_eic_value_map(map_csv, xml_path)

    assert output["MODSTitle"]
    assert output["MODSPlace"] == "Lha sa :"

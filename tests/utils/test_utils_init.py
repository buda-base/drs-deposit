from pathlib import Path


def test_utils_init_is_present() -> None:
    init_file = Path(__file__).resolve().parents[2] / "utils" / "__init__.py"
    assert init_file.exists()

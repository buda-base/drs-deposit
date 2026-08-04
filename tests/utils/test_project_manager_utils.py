import ast
from pathlib import Path


def test_project_manager_utils_declares_expected_api() -> None:
    source_path = Path(__file__).resolve().parents[2] / "utils" / "project_manager_utils.py"
    tree = ast.parse(source_path.read_text())

    classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}

    assert "pmItem" in classes
    assert {"_get_drs3_step_name", "get_next_work_pm_for_step", "get_pms_for_step", "update_database_from_pm_items"}.issubset(functions)

import ast
from pathlib import Path


def test_drs_db_declares_bootstrap_function() -> None:
    source_path = Path(__file__).resolve().parents[2] / "utils" / "drs_db.py"
    tree = ast.parse(source_path.read_text())
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert "create_drs3_project_with_steps" in functions

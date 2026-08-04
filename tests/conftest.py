import importlib
import os
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
UTILS_ROOT = REPO_ROOT / "utils"


@pytest.fixture(autouse=True)
def _prepend_repo_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(REPO_ROOT))
    monkeypatch.syspath_prepend(str(UTILS_ROOT))


@pytest.fixture
def load_utils_module(monkeypatch: pytest.MonkeyPatch):
    def _load(module_name: str, stubs: dict[str, Any] | None = None):
        sys.modules.pop(module_name, None)
        if stubs:
            for stub_name, stub in stubs.items():
                monkeypatch.setitem(sys.modules, stub_name, stub)
        return importlib.import_module(module_name)

    return _load


@pytest.fixture
def require_db_env() -> dict[str, str]:
    required = ("BDRC_DB_CNF", "BDRC_DB_PASSWORD")
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        pytest.skip(f"Missing required env vars: {', '.join(missing)}")
    return {key: os.environ[key] for key in required}

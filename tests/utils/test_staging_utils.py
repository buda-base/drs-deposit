# pyright: reportAttributeAccessIssue=false
import types
from pathlib import Path


def _build_stubs_for_staging(next_work):
    const_mod = types.ModuleType("const")
    const_mod.STAGE_STEP_NAME = "stage"
    const_mod.PROJECT_STEP_RESULT_CODE_KEY = "project_step_result_code"
    const_mod.PROJECT_STEP_START_TIME_KEY = "project_step_start_time"
    const_mod.PROJECT_STEP_END_TIME_KEY = "project_step_end_time"
    const_mod.get_work_image_path = lambda work_path: Path(work_path) / "images"

    pendulum_mod = types.ModuleType("pendulum")
    pendulum_mod.now = lambda _tz: "now"

    pm_mod = types.ModuleType("project_manager_utils")

    class _PmItem:
        def __init__(self, label, o_id):
            self.label = label
            self.o_id = o_id
            self.id = o_id
            self.extras = {}

    pm_mod.pmItem = _PmItem
    pm_mod._get_drs3_step_name = lambda name: f"step:{name}"
    pm_mod.get_next_work_pm_for_step = lambda *_args, **_kwargs: next_work
    pm_mod.get_pms_for_step = lambda *_args, **_kwargs: (_PmItem("W1", 1), [_PmItem("V001", 101)])
    pm_mod.update_database_from_pm_items = lambda *_args, **_kwargs: None

    return {
        "const": const_mod,
        "pendulum": pendulum_mod,
        "project_manager_utils": pm_mod,
    }


def test_stage_next_work_returns_none_when_no_candidate(load_utils_module) -> None:
    mod = load_utils_module("staging_utils", stubs=_build_stubs_for_staging(next_work=None))
    assert mod.stage_next_work("/src", "/staging") is None


def test_do_staging_sets_success_codes(monkeypatch, tmp_path: Path, load_utils_module) -> None:
    next_work = types.SimpleNamespace(label="W1", o_id=1, id=1, extras={})
    mod = load_utils_module("staging_utils", stubs=_build_stubs_for_staging(next_work=next_work))

    archive_api = types.ModuleType("archive_ops.api")
    archive_api.get_archive_location = lambda source_root, work_name: f"{source_root}/{work_name}"
    monkeypatch.setitem(__import__("sys").modules, "archive_ops.api", archive_api)
    monkeypatch.setattr("shutil.copytree", lambda *_args, **_kwargs: None)

    work = types.SimpleNamespace(label="W1", o_id=1, id=1, extras={})
    vols = [types.SimpleNamespace(label="V001", o_id=101, id=101, extras={})]

    mod.do_staging(work, vols, str(tmp_path / "src"), str(tmp_path / "staging"))

    assert work.extras["project_step_result_code"] == 0
    assert vols[0].extras["project_step_result_code"] == 0

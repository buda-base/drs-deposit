# pyright: reportAttributeAccessIssue=false
import types
from pathlib import Path


def _build_stubs_for_transcode(next_work):
    const_mod = types.ModuleType("const")
    const_mod.STAGE_STEP_NAME = "stage"
    const_mod.TRANSCODE_STEP_NAME = "transcode"
    const_mod.PROJECT_STEP_RESULT_CODE_KEY = "project_step_result_code"
    const_mod.PROJECT_STEP_START_TIME_KEY = "project_step_start_time"
    const_mod.PROJECT_STEP_END_TIME_KEY = "project_step_end_time"
    const_mod.get_work_image_path = lambda work_path: Path(work_path) / "images"
    const_mod.get_work_transcode_path = lambda work_path: Path(work_path) / "drs"

    pendulum_mod = types.ModuleType("pendulum")
    pendulum_mod.now = lambda _tz: "now"

    pm_mod = types.ModuleType("project_manager_utils")

    class _PmItem:
        def __init__(self, label, o_id):
            self.label = label
            self.o_id = o_id
            self.id = o_id
            self.extras = {}

    updates: list[tuple[_PmItem, list[_PmItem]]] = []
    transcode_calls: list[tuple[Path, Path]] = []

    pm_mod.pmItem = _PmItem
    pm_mod._get_drs3_step_name = lambda name: f"step:{name}"
    pm_mod.get_next_work_pm_for_step = lambda *_args, **_kwargs: next_work
    pm_mod.get_pms_for_step = lambda *_args, **_kwargs: (_PmItem("W1", 1), [_PmItem("V001", 101)])
    pm_mod.update_database_from_pm_items = lambda work, vols: updates.append((work, vols))

    transcode_mod = types.ModuleType("drs_pds_transcode")
    transcode_mod.transcode_volume = lambda src, dst: transcode_calls.append((src, dst))

    s3_mod = types.ModuleType("s3pathlib")

    class _S3Path(str):
        pass

    s3_mod.S3Path = _S3Path

    return (
        {
            "const": const_mod,
            "pendulum": pendulum_mod,
            "project_manager_utils": pm_mod,
            "drs_pds_transcode": transcode_mod,
            "s3pathlib": s3_mod,
        },
        updates,
        transcode_calls,
        _S3Path,
    )


def test_transcode_staged_volumes_returns_when_no_work(load_utils_module) -> None:
    stubs, _updates, _calls, _s3path = _build_stubs_for_transcode(next_work=None)
    mod = load_utils_module("transcode_utils", stubs=stubs)
    assert mod.transcode_staged_volumes("/staging") is None


def test_transcode_staged_volumes_updates_work_and_volumes(tmp_path: Path, load_utils_module) -> None:
    next_work = types.SimpleNamespace(label="W1", o_id=1, id=1, extras={})
    stubs, updates, transcode_calls, _s3path = _build_stubs_for_transcode(next_work=next_work)
    mod = load_utils_module("transcode_utils", stubs=stubs)

    mod.transcode_staged_volumes(str(tmp_path))

    assert transcode_calls
    assert updates
    work_item, volume_items = updates[0]
    assert work_item.extras["project_step_result_code"] == 0
    assert volume_items[0].extras["project_step_result_code"] == 0


def test_send_to_s3_accepts_paths(load_utils_module, tmp_path: Path) -> None:
    stubs, _updates, _calls, s3path = _build_stubs_for_transcode(next_work=None)
    mod = load_utils_module("transcode_utils", stubs=stubs)
    mod.send_to_s3(tmp_path / "file.jp2", s3path("s3://bucket/key"))

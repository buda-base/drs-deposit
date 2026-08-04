from pathlib import Path


def test_transcode_volume_skips_json(monkeypatch, tmp_path: Path, load_utils_module) -> None:
    mod = load_utils_module("drs_pds_transcode")

    volume_dir = tmp_path / "volume"
    out_dir = tmp_path / "out"
    volume_dir.mkdir()
    out_dir.mkdir()
    (volume_dir / "image-1.tif").write_text("x")
    (volume_dir / "meta.json").write_text("{}")

    calls: list[str] = []
    monkeypatch.setattr(mod, "convert_one", lambda fpath, drs_vol_path, fname: calls.append(fname))

    mod.transcode_volume(volume_dir, out_dir)

    assert calls == ["image-1.tif"]


def test_convert_one_copies_tiff(monkeypatch, load_utils_module) -> None:
    mod = load_utils_module("drs_pds_transcode")

    class _FakeImage:
        format = "TIFF"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    copied: list[tuple[str, str]] = []
    monkeypatch.setattr(mod.Image, "open", lambda _: _FakeImage())
    monkeypatch.setattr(mod.shutil, "copy2", lambda src, dst: copied.append((src, dst)))

    mod.convert_one("source.tif", "dest-dir", "source.tif")

    assert copied == [("source.tif", "dest-dir")]


def test_convert_one_writes_jp2(monkeypatch, load_utils_module) -> None:
    mod = load_utils_module("drs_pds_transcode")

    class _FakeImage:
        format = "PNG"
        width = 100
        height = 100

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def convert(self, _mode):
            return self

        def save(self, path, **kwargs):
            saved.append((path, kwargs))

    saved: list[tuple[str, dict]] = []
    monkeypatch.setattr(mod.Image, "open", lambda _: _FakeImage())
    monkeypatch.setattr(mod.os.path, "getsize", lambda _: 3000)

    mod.convert_one("source.png", "dest-dir", "source.png")

    assert saved
    assert saved[0][0].endswith("source.jp2")

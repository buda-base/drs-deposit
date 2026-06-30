import types


class _Field:
    def __eq__(self, other):  # noqa: D401
        return ("eq", other)


class _Select:
    def where(self, _expr):
        return self


def _build_stubs():
    archive_api = types.ModuleType("archive_ops.api")
    archive_api.get_archive_location = lambda archive_root, work_name: f"{archive_root}/{work_name}"

    drs_context = types.ModuleType("BdrcDbLib.DrsContext")

    class _DummyContext:
        def __init__(self, *_args, **_kwargs):
            self._session = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def get_session(self):
            return self._session

    drs_context.DrsDbContext = _DummyContext

    models = types.ModuleType("BdrcDbModels.models")
    models.Volumes = type("Volumes", (), {"label": _Field()})
    models.Works = type("Works", (), {"WorkName": _Field()})

    pm = types.ModuleType("BdrcDbModels.project_manager")
    pm.MemberTypes = type("MemberTypes", (), {"m_type": _Field()})
    pm.ProjectMembers = type("ProjectMembers", (), {})
    pm.Projects = type("Projects", (), {"name": _Field()})

    get_or_create_mod = types.ModuleType("BdrcDbModels.SqlAlchemy_get_or_create")
    get_or_create_mod.get_or_create = lambda *_args, **_kwargs: (object(), True)

    sqlalchemy_mod = types.ModuleType("sqlalchemy")
    sqlalchemy_mod.select = lambda *_args, **_kwargs: _Select()
    sqlalchemy_orm_mod = types.ModuleType("sqlalchemy.orm")
    sqlalchemy_orm_mod.Session = object

    return {
        "archive_ops.api": archive_api,
        "BdrcDbLib.DrsContext": drs_context,
        "BdrcDbModels.models": models,
        "BdrcDbModels.project_manager": pm,
        "BdrcDbModels.SqlAlchemy_get_or_create": get_or_create_mod,
        "sqlalchemy": sqlalchemy_mod,
        "sqlalchemy.orm": sqlalchemy_orm_mod,
    }


def test_select_member_type_uses_first_scalar(load_utils_module) -> None:
    mod = load_utils_module("populate_members", stubs=_build_stubs())

    expected = object()

    class _Result:
        def scalars(self):
            return self

        def first(self):
            return expected

    class _Session:
        def execute(self, _stmt):
            return _Result()

    assert mod._select_member_type(_Session(), "work") is expected

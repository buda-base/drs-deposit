import pytest


@pytest.mark.integration
def test_integration_env_vars_are_available(require_db_env: dict[str, str]) -> None:
    assert require_db_env["BDRC_DB_CNF"]
    assert require_db_env["BDRC_DB_PASSWORD"]

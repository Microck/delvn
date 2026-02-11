def test_settings_and_helpers_import() -> None:
    from config.settings import Settings  # noqa: F401
    from common.http import get_json  # noqa: F401

    assert True

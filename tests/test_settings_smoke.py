def test_settings_and_helpers_import() -> None:
    from common.http import build_client, get_json
    from config.settings import Settings

    settings = Settings()
    assert settings.APP_ENV == "dev"
    assert callable(get_json)

    with build_client() as client:
        assert client is not None

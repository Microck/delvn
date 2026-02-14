from __future__ import annotations

from config.user_stack import load_user_stack


def test_load_user_stack_defaults_missing_fields_to_empty_lists(tmp_path) -> None:
    config_path = tmp_path / "user_stack.yaml"
    config_path.write_text("products:\n  - Apache HTTP Server\n", encoding="utf-8")

    stack = load_user_stack(path=str(config_path))

    assert stack.products == ["Apache HTTP Server"]
    assert stack.platforms == []
    assert stack.exclude == []
    assert stack.keywords == []


def test_load_user_stack_normalizes_case_for_matching_and_dedupes() -> None:
    stack = load_user_stack(path="src/config/user_stack.yaml")

    assert stack.products == ["Apache HTTP Server", "PostgreSQL", "React"]
    assert stack.platforms == ["linux"]
    assert stack.exclude == ["windows"]
    assert stack.keywords == ["httpd", "postgres", "frontend"]
    assert stack.match_terms() == {
        "apache http server",
        "postgresql",
        "react",
        "linux",
        "httpd",
        "postgres",
        "frontend",
    }
    assert stack.exclude_terms() == {"windows"}


def test_load_user_stack_dedupes_case_insensitive_values_preserving_first_display(
    tmp_path,
) -> None:
    config_path = tmp_path / "user_stack.yaml"
    config_path.write_text(
        "\n".join(
            [
                "products:",
                "  - Apache HTTP Server",
                "  - apache http server",
                "platforms:",
                "  - Linux",
                "  - linux",
                "exclude:",
                "  - WINDOWS",
                "  - windows",
                "keywords:",
                "  - OpenSSL",
                "  - openssl",
            ]
        ),
        encoding="utf-8",
    )

    stack = load_user_stack(path=str(config_path))

    assert stack.products == ["Apache HTTP Server"]
    assert stack.platforms == ["Linux"]
    assert stack.exclude == ["WINDOWS"]
    assert stack.keywords == ["OpenSSL"]
    assert stack.match_terms() == {"apache http server", "linux", "openssl"}
    assert stack.exclude_terms() == {"windows"}

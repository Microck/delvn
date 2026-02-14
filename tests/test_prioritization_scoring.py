from __future__ import annotations

from config.user_stack import UserStack
from models.unified_threat import UnifiedThreat
from prioritization.scoring import Relevance, score_relevance


def test_score_relevance_product_match_is_medium() -> None:
    stack = UserStack(products=["PostgreSQL"], keywords=["postgres"])
    threat = _build_threat(
        title="PostgreSQL auth bypass bug",
        summary="Credential validation flaw in postgres extension",
        severity=5.4,
    )

    relevance, reasons = score_relevance(threat, stack)

    assert relevance is Relevance.MEDIUM
    assert any("product keyword match" in reason.lower() for reason in reasons)


def test_score_relevance_product_match_with_high_severity_is_high() -> None:
    stack = UserStack(products=["Apache HTTP Server"], keywords=["httpd"])
    threat = _build_threat(
        title="Apache HTTP Server remote code execution",
        summary="Critical RCE in mod_proxy",
        severity=9.1,
    )

    relevance, reasons = score_relevance(threat, stack)

    assert relevance is Relevance.HIGH
    assert any("severity" in reason.lower() for reason in reasons)


def test_score_relevance_no_match_is_none() -> None:
    stack = UserStack(products=["React"], keywords=["frontend"])
    threat = _build_threat(
        title="Windows SMB privilege escalation",
        summary="Affects legacy SMB services on Windows hosts",
        severity=6.0,
    )

    relevance, reasons = score_relevance(threat, stack)

    assert relevance is Relevance.NONE
    assert reasons


def test_score_relevance_returns_reasons_when_not_none() -> None:
    stack = UserStack(products=["PostgreSQL"])
    threat = _build_threat(
        title="PostgreSQL extension memory corruption",
        summary="Potential denial of service",
        severity=4.2,
    )

    relevance, reasons = score_relevance(threat, stack)

    assert relevance is Relevance.MEDIUM
    assert reasons


def _build_threat(
    *,
    title: str,
    summary: str,
    severity: float,
) -> UnifiedThreat:
    return UnifiedThreat.model_validate(
        {
            "id": "nvd:CVE-2026-0100",
            "source": "nvd",
            "type": "cve",
            "title": title,
            "summary": summary,
            "severity": severity,
            "raw": {"source": "nvd"},
        }
    )

from __future__ import annotations

from correlation.scoring import score_correlation


def test_score_correlation_is_monotonic_with_similarity() -> None:
    low_confidence, _ = score_correlation(
        similarity=0.2,
        shared_terms=1,
        same_source=False,
    )
    high_confidence, _ = score_correlation(
        similarity=0.8,
        shared_terms=1,
        same_source=False,
    )

    assert high_confidence > low_confidence


def test_shared_terms_boost_confidence_and_reasons() -> None:
    base_confidence, _ = score_correlation(
        similarity=0.55,
        shared_terms=0,
        same_source=False,
    )
    boosted_confidence, reasons = score_correlation(
        similarity=0.55,
        shared_terms=3,
        same_source=False,
    )

    assert boosted_confidence > base_confidence
    assert any("shared term boost" in reason.lower() for reason in reasons)


def test_score_correlation_clamps_confidence_to_unit_interval() -> None:
    high_confidence, _ = score_correlation(
        similarity=2.0,
        shared_terms=50,
        same_source=False,
    )
    low_confidence, _ = score_correlation(
        similarity=-3.0,
        shared_terms=0,
        same_source=True,
    )

    assert high_confidence == 1.0
    assert low_confidence == 0.0

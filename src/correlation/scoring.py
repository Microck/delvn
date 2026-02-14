from __future__ import annotations


def _clamp_01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def score_correlation(
    *, similarity: float, shared_terms: int, same_source: bool
) -> tuple[float, list[str]]:
    normalized_similarity = _clamp_01(similarity)
    bounded_shared_terms = max(shared_terms, 0)

    confidence = normalized_similarity * 0.85
    shared_terms_boost = min(bounded_shared_terms * 0.05, 0.2)
    confidence += shared_terms_boost

    reasons = [f"Vector similarity contribution: {normalized_similarity:.3f}"]
    if similarity != normalized_similarity:
        reasons.append("Similarity was clamped to the 0..1 range")

    if bounded_shared_terms > 0:
        reasons.append(
            "Shared term boost: "
            f"+{shared_terms_boost:.2f} from {bounded_shared_terms} overlapping terms"
        )

    if same_source:
        confidence -= 0.08
        reasons.append("Same-source penalty applied (-0.08)")
    else:
        reasons.append("Cross-source match boosts confidence diversity")

    confidence = _clamp_01(confidence)
    return confidence, reasons


__all__ = ["score_correlation"]

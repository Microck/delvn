from __future__ import annotations

from enum import Enum

from config.user_stack import UserStack
from models.unified_threat import UnifiedThreat


class Relevance(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


def score_relevance(
    threat: UnifiedThreat, stack: UserStack
) -> tuple[Relevance, list[str]]:
    content_text = threat.content_text().lower()

    product_terms = {value.lower() for value in stack.products if value}
    weak_terms = {
        value.lower() for value in [*stack.platforms, *stack.keywords] if value
    }
    weak_terms -= product_terms

    product_matches = _find_matches(content_text, product_terms)
    weak_matches = _find_matches(content_text, weak_terms)

    reasons: list[str] = []
    if product_matches:
        reasons.append(f"Product keyword match: {', '.join(product_matches)}")

    severity = threat.severity if threat.severity is not None else 0.0
    has_exploited_tag = any("exploited" in tag.lower() for tag in threat.tags)

    if product_matches and (severity >= 7.0 or has_exploited_tag):
        if severity >= 7.0:
            reasons.append(f"Severity {severity:.1f} is high (>= 7.0)")
        if has_exploited_tag:
            reasons.append("Threat is tagged as exploited")
        return Relevance.HIGH, reasons

    if product_matches:
        reasons.append("Product matched without high severity or exploited signal")
        return Relevance.MEDIUM, reasons

    if weak_matches:
        reasons.append(f"Weak keyword match: {', '.join(weak_matches)}")
        return Relevance.LOW, reasons

    return Relevance.NONE, ["No stack keyword matched threat content"]


def _find_matches(content_text: str, terms: set[str]) -> list[str]:
    return sorted(term for term in terms if term in content_text)


__all__ = ["Relevance", "score_relevance"]

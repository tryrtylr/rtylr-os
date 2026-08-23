"""Coverage analysis for the business-continuity acceptance catalog."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .scenarios import AcceptanceScenario


@dataclass(frozen=True)
class CoverageReport:
    scenario_count: int
    domain_counts: dict[str, int]
    condition_counts: dict[str, int]
    severity_counts: dict[str, int]
    status_counts: dict[str, int]
    admin_count: int
    offline_safe_count: int
    missing_pairs: tuple[str, ...]
    unexpected_pairs: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.missing_pairs and not self.unexpected_pairs


def analyze_coverage(
    scenarios: Iterable[AcceptanceScenario],
    expected_domains: Iterable[str],
    expected_conditions: Iterable[str],
) -> CoverageReport:
    items = list(scenarios)
    expected = {
        (domain, condition)
        for domain in expected_domains
        for condition in expected_conditions
    }
    actual = {(scenario.domain, scenario.condition) for scenario in items}
    missing = tuple(f"{domain}-{condition}" for domain, condition in sorted(expected - actual))
    unexpected = tuple(f"{domain}-{condition}" for domain, condition in sorted(actual - expected))
    return CoverageReport(
        scenario_count=len(items),
        domain_counts=dict(sorted(Counter(item.domain for item in items).items())),
        condition_counts=dict(sorted(Counter(item.condition for item in items).items())),
        severity_counts=dict(sorted(Counter(item.severity for item in items).items())),
        status_counts=dict(sorted(Counter(item.expected_status for item in items).items())),
        admin_count=sum(item.requires_admin for item in items),
        offline_safe_count=sum(item.offline_safe for item in items),
        missing_pairs=missing,
        unexpected_pairs=unexpected,
    )

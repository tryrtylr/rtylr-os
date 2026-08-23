#!/usr/bin/env python3
"""Require complete domain-by-condition acceptance coverage."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/rtylr-shell"))

from rtylr_shell.scenario_coverage import analyze_coverage  # noqa: E402
from rtylr_shell.scenarios import load_catalog  # noqa: E402


EXPECTED_DOMAINS = (
    "admin-pin",
    "agent",
    "application",
    "audio",
    "bluetooth",
    "boot",
    "clock",
    "configuration",
    "display",
    "dns",
    "ethernet",
    "filesystem",
    "gateway",
    "installer",
    "keyboard",
    "logs",
    "mouse",
    "network",
    "power",
    "printing",
    "session",
    "storage",
    "support",
    "thermal",
    "touchscreen",
    "updates",
    "usb",
    "wifi",
)
EXPECTED_CONDITIONS = (
    "degraded",
    "dependency-failed",
    "healthy-baseline",
    "intermittent",
    "misconfigured",
    "recovery-failed",
    "resource-exhausted",
    "timeout",
    "unavailable",
    "unsafe-state",
)


def main() -> int:
    scenarios = load_catalog(ROOT / "docs/acceptance/scenarios")
    report = analyze_coverage(scenarios, EXPECTED_DOMAINS, EXPECTED_CONDITIONS)
    print(
        f"Acceptance coverage: {report.scenario_count} scenarios; "
        f"{len(report.domain_counts)} domains; {len(report.condition_counts)} conditions; "
        f"admin={report.admin_count}; offline-safe={report.offline_safe_count}"
    )
    if not report.complete:
        for scenario_id in report.missing_pairs:
            print(f"Missing scenario: {scenario_id}", file=sys.stderr)
        for scenario_id in report.unexpected_pairs:
            print(f"Unexpected scenario: {scenario_id}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

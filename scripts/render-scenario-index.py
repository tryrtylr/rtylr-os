#!/usr/bin/env python3
"""Render the acceptance catalog as a review-friendly Markdown index."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/rtylr-shell"))

from rtylr_shell.scenarios import load_catalog  # noqa: E402


def render() -> str:
    scenarios = load_catalog(ROOT / "docs/acceptance/scenarios")
    grouped = defaultdict(list)
    for scenario in scenarios:
        grouped[scenario.domain].append(scenario)

    lines = [
        "# Acceptance scenario index",
        "",
        f"This generated index covers {len(scenarios)} validated scenarios across "
        f"{len(grouped)} business-device domains.",
        "",
        "Legend: **admin** requires the protected admin PIN; **offline-safe** means "
        "the scenario permits an explicitly verified local workflow.",
        "",
    ]
    for domain in sorted(grouped):
        title = domain.replace("-", " ").title()
        lines.extend((f"## {title}", ""))
        for scenario in sorted(grouped[domain], key=lambda item: item.condition):
            qualifiers = [scenario.severity, f"status:{scenario.expected_status}"]
            if scenario.requires_admin:
                qualifiers.append("admin")
            if scenario.offline_safe:
                qualifiers.append("offline-safe")
            detail = ", ".join(qualifiers)
            lines.append(
                f"- [{scenario.title}](scenarios/{scenario.scenario_id}.json) — {detail}"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the index is stale")
    arguments = parser.parse_args(argv)
    target = ROOT / "docs/acceptance/index.md"
    expected = render()
    if arguments.check:
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        if current != expected:
            print("Acceptance scenario index is stale.", file=sys.stderr)
            return 1
        print("Acceptance scenario index: current")
        return 0
    target.write_text(expected, encoding="utf-8")
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

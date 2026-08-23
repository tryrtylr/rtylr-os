#!/usr/bin/env python3
"""Validate the committed business-continuity acceptance catalog."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/rtylr-shell"))

from rtylr_shell.scenarios import ScenarioError, load_catalog  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    directory = (
        Path(arguments[0]).resolve()
        if arguments
        else ROOT / "docs/acceptance/scenarios"
    )
    try:
        scenarios = load_catalog(directory)
    except ScenarioError as exc:
        print(exc, file=sys.stderr)
        return 1

    domains = Counter(scenario.domain for scenario in scenarios)
    distribution = ", ".join(f"{name}={count}" for name, count in sorted(domains.items()))
    suffix = f" ({distribution})" if distribution else ""
    print(f"Acceptance scenarios: {len(scenarios)} valid{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

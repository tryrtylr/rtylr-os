"""Strict acceptance-scenario loading for business-continuity testing."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Mapping


SCHEMA_VERSION = 1
VALID_SEVERITIES = frozenset({"info", "warning", "error", "critical"})
VALID_STATUSES = frozenset({"ok", "warning", "error", "neutral"})
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ScenarioError(ValueError):
    """Raised when an acceptance scenario is malformed."""


@dataclass(frozen=True)
class AcceptanceScenario:
    scenario_id: str
    domain: str
    condition: str
    title: str
    severity: str
    expected_status: str
    requires_admin: bool
    offline_safe: bool
    signals: tuple[str, ...]
    operator_steps: tuple[str, ...]
    admin_steps: tuple[str, ...]
    success_criteria: tuple[str, ...]
    tags: tuple[str, ...]
    source: str


def _text(value: Any, field: str, source: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScenarioError(f"{source}: {field} must be a non-empty string")
    return value.strip()


def _slug(value: Any, field: str, source: str) -> str:
    text = _text(value, field, source)
    if not SLUG.fullmatch(text):
        raise ScenarioError(f"{source}: {field} must be a lowercase slug")
    return text


def _text_list(
    value: Any,
    field: str,
    source: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a string array" if allow_empty else "a non-empty string array"
        raise ScenarioError(f"{source}: {field} must be {qualifier}")
    result = tuple(_text(item, f"{field}[]", source) for item in value)
    if len(set(result)) != len(result):
        raise ScenarioError(f"{source}: {field} must not contain duplicates")
    return result


def parse_scenario(payload: Mapping[str, Any], source: str = "<memory>") -> AcceptanceScenario:
    if not isinstance(payload, Mapping):
        raise ScenarioError(f"{source}: scenario must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ScenarioError(f"{source}: schema_version must be {SCHEMA_VERSION}")

    scenario_id = _slug(payload.get("id"), "id", source)
    domain = _slug(payload.get("domain"), "domain", source)
    condition = _slug(payload.get("condition"), "condition", source)
    if scenario_id != f"{domain}-{condition}":
        raise ScenarioError(f"{source}: id must equal <domain>-<condition>")

    severity = _text(payload.get("severity"), "severity", source)
    if severity not in VALID_SEVERITIES:
        raise ScenarioError(f"{source}: unsupported severity {severity!r}")
    expected_status = _text(payload.get("expected_status"), "expected_status", source)
    if expected_status not in VALID_STATUSES:
        raise ScenarioError(f"{source}: unsupported expected_status {expected_status!r}")

    requires_admin = payload.get("requires_admin")
    offline_safe = payload.get("offline_safe")
    if not isinstance(requires_admin, bool) or not isinstance(offline_safe, bool):
        raise ScenarioError(f"{source}: requires_admin and offline_safe must be booleans")

    admin_steps = _text_list(
        payload.get("admin_steps"),
        "admin_steps",
        source,
        allow_empty=not requires_admin,
    )
    if requires_admin and not admin_steps:
        raise ScenarioError(f"{source}: protected scenarios require admin_steps")

    return AcceptanceScenario(
        scenario_id=scenario_id,
        domain=domain,
        condition=condition,
        title=_text(payload.get("title"), "title", source),
        severity=severity,
        expected_status=expected_status,
        requires_admin=requires_admin,
        offline_safe=offline_safe,
        signals=_text_list(payload.get("signals"), "signals", source),
        operator_steps=_text_list(payload.get("operator_steps"), "operator_steps", source),
        admin_steps=admin_steps,
        success_criteria=_text_list(
            payload.get("success_criteria"), "success_criteria", source
        ),
        tags=_text_list(payload.get("tags"), "tags", source),
        source=source,
    )


def load_scenario(path: Path) -> AcceptanceScenario:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioError(f"{path}: could not read scenario: {exc}") from exc
    return parse_scenario(payload, str(path))


def load_catalog(directory: Path) -> list[AcceptanceScenario]:
    scenarios = [load_scenario(path) for path in sorted(directory.glob("*.json"))]
    seen: dict[str, str] = {}
    for scenario in scenarios:
        if scenario.scenario_id in seen:
            raise ScenarioError(
                f"{scenario.source}: duplicate id also defined by {seen[scenario.scenario_id]}"
            )
        seen[scenario.scenario_id] = scenario.source
    return scenarios

import json
from pathlib import Path
import tempfile
import unittest

from rtylr_shell.scenarios import ScenarioError, load_catalog, load_scenario, parse_scenario


def valid_payload(**overrides):
    payload = {
        "schema_version": 1,
        "id": "network-unavailable",
        "domain": "network",
        "condition": "unavailable",
        "title": "Network is unavailable",
        "severity": "critical",
        "expected_status": "error",
        "requires_admin": True,
        "offline_safe": False,
        "signals": ["Network health reports Offline"],
        "operator_steps": ["Open Recovery & settings"],
        "admin_steps": ["Reconnect networking from the System page"],
        "success_criteria": ["Network health reports Connected"],
        "tags": ["continuity", "network"],
    }
    payload.update(overrides)
    return payload


class ScenarioTests(unittest.TestCase):
    def test_parses_valid_scenario(self):
        scenario = parse_scenario(valid_payload())
        self.assertEqual(scenario.scenario_id, "network-unavailable")
        self.assertTrue(scenario.requires_admin)
        self.assertEqual(scenario.signals, ("Network health reports Offline",))

    def test_rejects_non_slug_identifier(self):
        with self.assertRaisesRegex(ScenarioError, "lowercase slug"):
            parse_scenario(valid_payload(id="Network Unavailable"))

    def test_identifier_must_match_domain_and_condition(self):
        with self.assertRaisesRegex(ScenarioError, "<domain>-<condition>"):
            parse_scenario(valid_payload(id="network-offline"))

    def test_protected_scenario_requires_admin_steps(self):
        with self.assertRaisesRegex(ScenarioError, "admin_steps"):
            parse_scenario(valid_payload(admin_steps=[]))

    def test_unprotected_scenario_allows_empty_admin_steps(self):
        scenario = parse_scenario(
            valid_payload(requires_admin=False, admin_steps=[], severity="info")
        )
        self.assertEqual(scenario.admin_steps, ())

    def test_rejects_unknown_fields(self):
        with self.assertRaisesRegex(ScenarioError, "unknown fields"):
            parse_scenario(valid_payload(guess="not allowed"))

    def test_rejects_non_slug_tags(self):
        with self.assertRaisesRegex(ScenarioError, "lowercase slugs"):
            parse_scenario(valid_payload(tags=["continuity", "Needs Review"]))

    def test_file_name_must_match_identifier(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "different-name.json"
            path.write_text(json.dumps(valid_payload()), encoding="utf-8")
            with self.assertRaisesRegex(ScenarioError, "file name"):
                load_scenario(path)

    def test_catalog_rejects_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("one.json", "two.json"):
                (root / name).write_text(json.dumps(valid_payload()), encoding="utf-8")
            with self.assertRaisesRegex(ScenarioError, "duplicate id"):
                load_catalog(root)


if __name__ == "__main__":
    unittest.main()

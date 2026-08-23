import unittest

from rtylr_shell.scenario_coverage import analyze_coverage
from rtylr_shell.scenarios import parse_scenario


def scenario(domain, condition, *, admin=False, offline=False, severity="warning"):
    return parse_scenario(
        {
            "schema_version": 1,
            "id": f"{domain}-{condition}",
            "domain": domain,
            "condition": condition,
            "title": f"{domain} {condition}",
            "severity": severity,
            "expected_status": "warning",
            "requires_admin": admin,
            "offline_safe": offline,
            "signals": ["Visible signal"],
            "operator_steps": ["Safe operator step"],
            "admin_steps": ["Protected step"] if admin else [],
            "success_criteria": ["Visible success"],
            "tags": ["continuity"],
        }
    )


class ScenarioCoverageTests(unittest.TestCase):
    def test_complete_matrix(self):
        scenarios = [
            scenario(domain, condition)
            for domain in ("application", "network")
            for condition in ("healthy", "unavailable")
        ]
        report = analyze_coverage(
            scenarios,
            ("application", "network"),
            ("healthy", "unavailable"),
        )
        self.assertTrue(report.complete)
        self.assertEqual(report.scenario_count, 4)

    def test_reports_missing_pairs(self):
        report = analyze_coverage(
            [scenario("network", "healthy")],
            ("network",),
            ("healthy", "unavailable"),
        )
        self.assertEqual(report.missing_pairs, ("network-unavailable",))

    def test_reports_unexpected_pairs(self):
        report = analyze_coverage(
            [scenario("network", "healthy"), scenario("network", "unknown")],
            ("network",),
            ("healthy",),
        )
        self.assertEqual(report.unexpected_pairs, ("network-unknown",))

    def test_counts_policy_flags(self):
        report = analyze_coverage(
            [
                scenario("storage", "degraded", offline=True),
                scenario("storage", "unavailable", admin=True, severity="critical"),
            ],
            ("storage",),
            ("degraded", "unavailable"),
        )
        self.assertEqual(report.admin_count, 1)
        self.assertEqual(report.offline_safe_count, 1)
        self.assertEqual(report.severity_counts, {"critical": 1, "warning": 1})


if __name__ == "__main__":
    unittest.main()

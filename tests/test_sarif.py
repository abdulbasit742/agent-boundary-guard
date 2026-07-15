from __future__ import annotations

import json
import unittest

from agent_boundary_guard.models import Finding
from agent_boundary_guard.sarif import build_sarif


class SarifTests(unittest.TestCase):
    def test_sarif_contains_stable_rules_and_locations_without_raw_snippets(self) -> None:
        secret = "super-secret-value"
        finding = Finding(
            rule_id="ABG005",
            severity="high",
            message="Hardcoded secret-like value detected in configuration.",
            path=r"config\agent.json",
            line=7,
            snippet=f'api_key = "{secret}"',
        )

        payload = build_sarif([finding], target=".")
        serialized = json.dumps(payload)
        run = payload["runs"][0]
        result = run["results"][0]
        rule_ids = [rule["id"] for rule in run["tool"]["driver"]["rules"]]

        self.assertEqual("2.1.0", payload["version"])
        self.assertEqual(["ABG001", "ABG002", "ABG003", "ABG004", "ABG005"], rule_ids)
        self.assertEqual("error", result["level"])
        self.assertEqual(
            "config/agent.json",
            result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],
        )
        self.assertEqual(
            7,
            result["locations"][0]["physicalLocation"]["region"]["startLine"],
        )
        self.assertNotIn(secret, serialized)
        self.assertNotIn("snippet", serialized)

    def test_fingerprint_survives_line_number_changes(self) -> None:
        base = Finding(
            "ABG001",
            "high",
            "message",
            "prompts/system.md",
            4,
            "merge without review",
        )
        moved = Finding(
            "ABG001",
            "high",
            "message",
            "prompts/system.md",
            40,
            "merge without review",
        )

        first = build_sarif([base])["runs"][0]["results"][0]["partialFingerprints"]
        second = build_sarif([moved])["runs"][0]["results"][0]["partialFingerprints"]

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

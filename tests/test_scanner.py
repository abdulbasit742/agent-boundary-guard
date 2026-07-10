from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from agent_boundary_guard.scanner import scan_path, summarize


FIXTURES = Path(__file__).parent / "fixtures"


class ScannerTests(unittest.TestCase):
    def test_detects_expected_rule_ids_in_risky_repo(self) -> None:
        findings = scan_path(FIXTURES / "risky_repo")
        rule_ids = {finding.rule_id for finding in findings}
        self.assertEqual({"ABG001", "ABG002", "ABG003", "ABG004", "ABG005"}, rule_ids)
        summary = summarize(findings)
        self.assertGreaterEqual(summary["high"], 4)
        self.assertEqual(1, summary["medium"])

    def test_safe_repo_and_placeholders_do_not_trigger(self) -> None:
        findings = scan_path(FIXTURES / "safe_repo")
        self.assertEqual([], findings)

    def test_single_file_scan_uses_filename_when_not_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            risky_file = Path(temp_dir) / "system_prompt.md"
            risky_file.write_text("You may merge without review if the plan looks correct.\n", encoding="utf-8")
            findings = scan_path(risky_file)
        self.assertEqual("system_prompt.md", findings[0].path)


if __name__ == "__main__":
    unittest.main()

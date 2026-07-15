from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from agent_boundary_guard.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


class CliTests(unittest.TestCase):
    def test_json_output_and_nonzero_exit_for_risky_repo(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "scan",
                    str(FIXTURES / "risky_repo"),
                    "--format",
                    "json",
                    "--fail-on",
                    "high",
                ]
            )
        payload = json.loads(buffer.getvalue())
        self.assertEqual(1, exit_code)
        self.assertEqual(6, payload["finding_count"])
        self.assertEqual(5, payload["summary"]["high"])
        self.assertEqual(1, payload["summary"]["medium"])

    def test_text_output_and_zero_exit_for_safe_repo(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "scan",
                    str(FIXTURES / "safe_repo"),
                    "--format",
                    "text",
                    "--fail-on",
                    "high",
                ]
            )
        output = buffer.getvalue()
        self.assertEqual(0, exit_code)
        self.assertIn("Agent Boundary Guard: 0 finding(s)", output)
        self.assertIn("Summary: critical=0 high=0 medium=0 low=0", output)

    def test_sarif_output_file_is_written_before_threshold_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "reports" / "agent-boundary-guard.sarif"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exit_code = main(
                    [
                        "scan",
                        str(FIXTURES / "risky_repo"),
                        "--format",
                        "sarif",
                        "--output",
                        str(output),
                        "--fail-on",
                        "high",
                    ]
                )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(1, exit_code)
        self.assertEqual("", buffer.getvalue())
        self.assertEqual("2.1.0", payload["version"])
        self.assertEqual(6, len(payload["runs"][0]["results"]))


if __name__ == "__main__":
    unittest.main()
